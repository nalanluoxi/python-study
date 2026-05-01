import json
import threading
from pathlib import Path

from py.PythonTest.claude学习 import TOOL_package
from py.PythonTest.claude学习.MessageBus import MessageBus
from py.PythonTest.claude学习.ToolFunction import ToolFunction


class TeammateManager:

    dir: Path
    config_path: Path
    config: dict
    threads: dict
    BUS: MessageBus
    client: object
    model: str
    workdir: Path
    tool_function: ToolFunction
    _base_handlers: dict
    shutdown_requests = {}
    plan_requests = {}
    _tracker_lock = threading.Lock()
    # ── Condition 注册表（类比 Java ReentrantLock.newCondition）──────
    # { req_id: {"condition": Condition, "result": None | dict} }
    # 成员提交计划后在 condition 上 wait()，队长审批后 notify_all() 唤醒
    _plan_conditions: dict

    def __init__(self, team_dir: Path, bus_dir: Path, client, model: str, workdir: Path,
                 tool_function: ToolFunction):
        self.dir = team_dir
        self.dir.mkdir(exist_ok=True)
        self.config_path = self.dir / "config.json"
        self.config = self._load_config()
        self.threads = {}
        self.BUS = MessageBus(bus_dir)
        self.client = client
        self.model = model
        self.workdir = workdir
        self.tool_function = tool_function
        self._base_handlers = self.tool_function._build_nomal_handlers()
        self._plan_conditions = {}   # { req_id: {"condition": Condition, "result": None|dict} }

    # ── 配置 ─────────────────────────────────────────────────────
    def _load_config(self) -> dict:
        if self.config_path.exists():
            text = self.config_path.read_text().strip()
            if text:
                return json.loads(text)
        return {"team_name": "default", "members": []}

    def _save_config(self):
        self.config_path.write_text(json.dumps(self.config, indent=2, ensure_ascii=False))

    def _find_member(self, name: str):
        for item in self.config["members"]:
            if item["name"] == name:
                return item
        return None

    # ── 成员管理 ─────────────────────────────────────────────────
    def spawn(self, name: str, role: str, prompt: str) -> str:
        member = self._find_member(name)
        if member:
            if member["status"] not in ("idle", "shutdown"):
                return f"Error: '{name}' 状态为 {member['status']},不可执行"
            member["status"] = "working"
            member["role"] = role
        else:
            member = {"name": name, "role": role, "status": "working"}
            self.config["members"].append(member)
        self._save_config()
        thread = threading.Thread(
            target=self._teammate_loop,
            args=(name, role, prompt),
            daemon=True,
        )
        self.threads[name] = thread
        thread.start()
        return f"生成 '{name}' (role: {role})"

    def list_all(self) -> str:
        if not self.config["members"]:
            return "No teammates."
        lines = [f"Team: {self.config['team_name']}"]
        for m in self.config["members"]:
            lines.append(f"  {m['name']} ({m['role']}): {m['status']}")
        return "\n".join(lines)

    def member_names(self) -> list:
        return [m["name"] for m in self.config["members"]]

    # ── Agent 主循环 ──────────────────────────────────────────────
    def _teammate_loop(self, name: str, role: str, prompt: str):
        sys_prompt = (
            f"你是 '{name}', 角色: {role}, 工作目录: {self.workdir}. "
            f"使用 send_message 进行通信。完成你的任务。"
            f"发送消息给队长时，to 字段必须填写 'lead'（不是'队长'或其他名称）。"
            f"使用 shutdown_response 响应 shutdown_request。"
            f"重要：调用 plan_approval 提交计划后立即停止，系统会在审批完成后自动唤醒你继续执行。"
            f"注意：此系统为 macOS，执行 Python 脚本须使用 python3 命令，不能使用 python。"
            f"重要：任务完成后必须立即停止，不要继续轮询邮箱或重复执行操作。完成任务的标志是用 send_message 向队长汇报结果后直接结束。"
        )
        messages = [{"role": "user", "content": prompt}]
        tools = TOOL_package.TEAMMATE_TOOLS
        should_exit = False

        for _ in range(50):
            # 读邮箱，把新消息注入对话上下文
            inbox = self.BUS.read_inbox(name)
            for msg in inbox:
                messages.append({"role": "user", "content": json.dumps(msg, ensure_ascii=False)})
            if should_exit:
                break
            try:
                response = self.client.messages.create(
                    model=self.model, system=sys_prompt,
                    messages=messages, tools=tools, max_tokens=8000,
                )
            except Exception:
                break
            messages.append({"role": "assistant", "content": [b.model_dump() for b in response.content]})
            if response.stop_reason != "tool_use":
                break
            results = []
            need_compress = False
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if block.name == "compact":
                    need_compress = True
                    output = "压缩中..."
                else:
                    output = self._exec(name, block.name, block.input)
                print(f"  [{name}] {block.name}: {str(output)[:120]}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output),
                })
                if block.name == "shutdown_response" and block.input.get("approve"):
                    should_exit = True
                # ── 计划审批：在 Condition 上 wait()，线程真正挂起 ──────────────
                # 对应 Java: condition.await()
                if block.name == "plan_approval":
                    req_id = self._extract_req_id(str(output))
                    if req_id and req_id in self._plan_conditions:
                        entry = self._plan_conditions[req_id]
                        cond = entry["condition"]
                        with cond:
                            # wait() 会原子地释放锁并挂起线程，直到 notify_all() 唤醒
                            # 对应 Java: lock.lock(); condition.await(); lock.unlock()
                            cond.wait()
                        # 被唤醒后，把审批结果注入对话上下文
                        result = entry.get("result") or {}
                        approve = result.get("approve", False)
                        feedback = result.get("feedback", "")
                        status_msg = "已批准，请继续执行" if approve else f"已拒绝：{feedback}"
                        messages.append({"role": "user", "content": f"[计划审批结果] {status_msg}"})
                        with self._tracker_lock:
                            self._plan_conditions.pop(req_id, None)
            messages.append({"role": "user", "content": results})
            if need_compress:
                messages[:] = self.tool_function.auto_compress(messages)
        member = self._find_member(name)
        if member:
            final_status = "shutdown" if should_exit else "idle"
            member["status"] = final_status
            self._save_config()
            # 任务结束后主动通知队长，否则队长只能靠轮询等待
            self.BUS.send(name, "lead", f"我已完成任务，当前状态: {final_status}", "message")

    # ── 工具分发 ──────────────────────────────────────────────────
    def _exec(self, sender: str, tool_name: str, args: dict) -> str:
        sender_handlers = {
            # 发消息：WORKDIR/.bus/{to}.jsonl
            "send_message": lambda **kw: self.BUS.send(sender, kw["to"], kw["content"], kw.get("msg_type", "message")),
            # 读自己邮箱：WORKDIR/.bus/{sender}.jsonl
            "read_inbox":   lambda **kw: json.dumps(self.BUS.read_inbox(sender), ensure_ascii=False),
            # 回复关闭请求：写入队长邮箱 WORKDIR/.bus/lead.jsonl
            "shutdown_response": lambda **kw: self._handle_shutdown_response(sender, kw["request_id"], kw["approve"], kw.get("reason", "")),
            # 提交计划审批：写入队长邮箱 WORKDIR/.bus/lead.jsonl
            "plan_approval": lambda **kw: self._handle_plan_approval(sender, kw["plan"]),
        }
        handler = sender_handlers.get(tool_name) or self._base_handlers.get(tool_name)
        return handler(**args) if handler else f"Unknown tool: {tool_name}"

    def _extract_req_id(self, output: str) -> str:
        """从工具返回值里提取 request_id=xxxx"""
        import re
        m = re.search(r"request_id=([0-9a-f]+)", output)
        return m.group(1) if m else None

    def _handle_shutdown_response(self, sender: str, request_id: str, approve: bool, reason: str) -> str:
        """成员回复关闭请求，消息发往队长邮箱：WORKDIR/.bus/lead.jsonl"""
        self.BUS.send(sender, "lead", reason or "确认关闭", "shutdown_response",
                      {"request_id": request_id, "approve": approve})
        return f"关闭{'批准' if approve else '拒绝'}"

    def _handle_plan_approval(self, sender: str, plan: str) -> str:
        """
        成员提交计划审批。
        1. 生成 req_id，注册一个 Condition（对应 Java: lock.newCondition()）
        2. 把计划发到队长邮箱
        3. 返回 req_id 给调用方，调用方在 Condition 上 wait() 挂起线程
        """
        import uuid
        req_id = str(uuid.uuid4())[:8]
        # 提前注册 Condition，确保队长 notify 时能找到对应条目
        # 对应 Java: Condition cond = lock.newCondition();
        cond = threading.Condition(threading.Lock())
        with self._tracker_lock:
            self.plan_requests[req_id] = {"from": sender, "plan": plan, "status": "pending"}
            self._plan_conditions[req_id] = {"condition": cond, "result": None}
        # 通知队长：收件人 "lead"，邮箱文件 WORKDIR/.bus/lead.jsonl
        self.BUS.send(sender, "lead", plan, "plan_approval_response",
                      {"request_id": req_id, "plan": plan})
        return f"计划已提交 request_id={req_id}，线程将挂起等待队长审批"

    def notify_plan_result(self, req_id: str, approve: bool, feedback: str = ""):
        """
        队长审批完成后调用，唤醒等待中的成员线程。
        对应 Java: condition.signalAll()
        """
        with self._tracker_lock:
            entry = self._plan_conditions.get(req_id)
        if not entry:
            return
        entry["result"] = {"approve": approve, "feedback": feedback}
        cond = entry["condition"]
        with cond:
            # notify_all() 唤醒所有在此 Condition 上 wait() 的线程
            # 对应 Java: condition.signalAll()
            cond.notify_all()