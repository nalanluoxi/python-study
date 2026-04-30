import json
import subprocess
import time
from pathlib import Path

from py.PythonTest.claude学习.MessageBus import MessageBus

DANGEROUS_COMMANDS = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]


class ToolFunction:

    WORKDIR: Path
    TRANSCRIPT_DIR: Path
    _todo: object
    _skill_loader: object
    _task_manager: object
    _bg_manager: object
    _client: object
    _model: str
    _subagent_system: str
    _nomal_tools: list
    _nomal_handlers: dict
    _parent_handlers: dict
    _keep_max_len: int
    _max_token_len: int
    _preserve_result_tools: set

    def __init__(self, workdir: Path, todo, skill_loader, task_manager, bg_manager,
                 client, model: str, subagent_system: str, nomal_tools: list,
                 transcript_dir: Path, keep_max_len: int = 3,
                 max_token_len: int = 50_000, preserve_result_tools: set = None):
        self.WORKDIR = workdir
        self.TRANSCRIPT_DIR = transcript_dir
        self._todo = todo
        self._skill_loader = skill_loader
        self._task_manager = task_manager
        self._bg_manager = bg_manager
        self._client = client
        self._model = model
        self._subagent_system = subagent_system
        self._nomal_tools = nomal_tools
        self._keep_max_len = keep_max_len
        self._max_token_len = max_token_len
        self._preserve_result_tools = preserve_result_tools or {"read_file"}
        self._nomal_handlers = self._build_nomal_handlers()
        self._parent_handlers = self._build_parent_handlers()

    # ── 分发表构建 ───────────────────────────────────────────────
    def _build_nomal_handlers(self) -> dict:
        return {
            "bash":             lambda **kw: self._run_bash(kw["command"]),
            "read_file":        lambda **kw: self._run_read(kw["path"], kw.get("limit")),
            "write_file":       lambda **kw: self._run_write(kw["path"], kw["content"]),
            "edit_file":        lambda **kw: self._run_edit(kw["path"], kw["old_text"], kw["new_text"]),
            "todo_tool":        lambda **kw: self._todo.update(kw["items"]),
            "load_skill":       lambda **kw: self._skill_loader.get_content(kw["name"]),
            "compact":          lambda **kw: "请求手动压缩",
            "task_create":      lambda **kw: self._task_manager.create(kw["subject"], kw.get("description", "")),
            "task_update":      lambda **kw: self._task_manager.update(kw["task_id"], kw.get("status"), kw.get("add_blocked_by"), kw.get("remove_blocked_by")),
            "task_get":         lambda **kw: self._task_manager.get(kw["task_id"]),
            "task_get_all":     lambda **kw: self._task_manager.list_all(),
            "background_run":   lambda **kw: self._bg_manager.run(kw["command"]),
            "check_background": lambda **kw: self._bg_manager.check(kw.get("task_id")),
        }

    def _build_parent_handlers(self) -> dict:
        return {
            **self._nomal_handlers,
            "build_child_task": lambda **kw: self.run_subagent(kw["prompt"]),
        }

    def dispatch_nomal(self, tool_name: str, args: dict) -> str:
        handler = self._nomal_handlers.get(tool_name)
        return handler(**args) if handler else f"Unknown tool: {tool_name}"

    def dispatch_parent(self, tool_name: str, args: dict) -> str:
        handler = self._parent_handlers.get(tool_name)
        return handler(**args) if handler else f"Unknown tool: {tool_name}"

    # ── 安全路径校验 ─────────────────────────────────────────────
    def _safe_path(self, p: str) -> Path:
        path = (self.WORKDIR / p).resolve()
        print(f"路径检查: {path}")
        if not path.is_relative_to(self.WORKDIR):
            raise ValueError(f"路径越界: {p}")
        return path

    # ── 工具实现 ─────────────────────────────────────────────────
    def _run_bash(self, command: str) -> str:
        if any(d in command for d in DANGEROUS_COMMANDS):
            return "Error: Dangerous command blocked"
        try:
            r = subprocess.run(command, shell=True, cwd=self.WORKDIR,
                               capture_output=True, text=True, timeout=120,
                               encoding="utf-8", errors="replace")
            out = (r.stdout + r.stderr).strip()
            return out[:50_000] if out else "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Timeout (120s)"
        except Exception as e:
            return f"Error: {e}"

    def _run_read(self, path: str, limit: int = None) -> str:
        try:
            lines = self._safe_path(path).read_text().splitlines()
            if limit and limit < len(lines):
                lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
            return "\n".join(lines)[:50_000]
        except Exception as e:
            return f"Error: {e}"

    def _run_write(self, path: str, content: str) -> str:
        try:
            fp = self._safe_path(path)
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content)
            return f"Wrote {len(content)} bytes to {path}"
        except Exception as e:
            return f"Error: {e}"

    def _run_edit(self, path: str, old_text: str, new_text: str) -> str:
        try:
            fp = self._safe_path(path)
            content = fp.read_text()
            if old_text not in content:
                return f"Error: Text not found in {path}"
            fp.write_text(content.replace(old_text, new_text, 1))
            return f"Edited {path}"
        except Exception as e:
            return f"Error: {e}"

    # ── 子 Agent ─────────────────────────────────────────────────
    def run_subagent(self, prompt: str) -> str:
        sub_messages = [{"role": "user", "content": prompt}]
        for _ in range(30):
            response = self._client.messages.create(
                model=self._model, system=self._subagent_system,
                messages=sub_messages,
                tools=self._nomal_tools, max_tokens=8000,
            )
            sub_messages.append({"role": "assistant", "content": [b.model_dump() for b in response.content]})
            if response.stop_reason != "tool_use":
                break
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    output = self.dispatch_nomal(block.name, block.input)
                    results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)[:50_000]})
            sub_messages.append({"role": "user", "content": results})
        return "".join(b.text for b in response.content if hasattr(b, "text")) or "(no summary)"

    # ── 上下文压缩 ───────────────────────────────────────────────
    def estimate_token(self, message: list) -> int:
        return len(str(message)) // 4 + 1

    def micro_compact(self, message: list) -> list:
        tool_results = [
            (mi, ci, data)
            for mi, msg in enumerate(message)
            if msg["role"] == "user" and isinstance(msg["content"], list)
            for ci, data in enumerate(msg["content"])
            if isinstance(data, dict) and data.get("type") == "tool_result"
        ]
        if len(tool_results) <= self._keep_max_len:
            return message
        tool_name_map = {
            item.id: item.name
            for msg in message
            if msg["role"] == "assistant" and isinstance(msg.get("content"), list)
            for item in msg["content"]
            if hasattr(item, "type") and item.type == "tool_use"
        }
        for _, _, item in tool_results[:-self._keep_max_len]:
            content = item.get("content")
            if not isinstance(content, list) or len(content) <= 100:
                continue
            tool_name = tool_name_map.get(item.get("tool_use_id", ""), "")
            if tool_name in self._preserve_result_tools:
                continue
            item["content"] = f"[以前使用了工具:{tool_name}]"
        return message

    def auto_compress(self, message: list) -> list:
        self.TRANSCRIPT_DIR.mkdir(exist_ok=True)
        trans_path = self.TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
        with open(trans_path, "w") as f:
            for msg in message:
                f.write(json.dumps(msg, default=str) + "\n")
        print(f"[历史保存到路径: {trans_path}]")
        data = json.dumps(message, default=str)[-80_000:]
        response = self._client.messages.create(
            model=self._model,
            messages=[{"role": "user", "content": (
                "为了保持对话的连贯性，请总结本次对话。内容包括：\n"
                "1) 已完成的工作，2) 当前状况，3) 已做出的关键决策。\n\n"
                "下面是对话内容\n" + data
            )}],
            max_tokens=2000,
        )
        summary = next((item.text for item in response.content if hasattr(item, "text")), "未生成摘要")
        return [{"role": "user", "content": f"[对话内容精简版。文字稿: {trans_path}]\n\n{summary}"}]