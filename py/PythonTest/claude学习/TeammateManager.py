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

    # ── 配置 ─────────────────────────────────────────────────────
    def _load_config(self) -> dict:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {"team_name": "default", "members": []}

    def _save_config(self):
        self.config_path.write_text(json.dumps(self.config, indent=2))

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
        )
        messages = [{"role": "user", "content": prompt}]
        tools = TOOL_package.TEAMMATE_TOOLS
        for _ in range(50):
            inbox = self.BUS.read_inbox(name)
            for msg in inbox:
                messages.append({"role": "user", "content": json.dumps(msg)})
            try:
                response = self.client.messages.create(
                    model=self.model, system=sys_prompt,
                    messages=messages, tools=tools, max_tokens=8000,
                )
            except Exception:
                break
            messages.append({"role": "assistant", "content": response.content})
            if response.stop_reason != "tool_use":
                break
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    output = self._exec(name, block.name, block.input)
                    print(f"  [{name}] {block.name}: {str(output)[:120]}")
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(output),
                    })
            messages.append({"role": "user", "content": results})
        member = self._find_member(name)
        if member and member["status"] != "shutdown":
            member["status"] = "idle"
            self._save_config()

    # ── 工具分发 ──────────────────────────────────────────────────
    def _exec(self, sender: str, tool_name: str, args: dict) -> str:
        sender_handlers = {
            "send_message": lambda **kw: self.BUS.send(sender, kw["to"], kw["content"], kw.get("msg_type", "message")),
            "read_inbox":   lambda **kw: json.dumps(self.BUS.read_inbox(sender), indent=2),
        }
        handler = sender_handlers.get(tool_name) or self._base_handlers.get(tool_name)
        return handler(**args) if handler else f"Unknown tool: {tool_name}"