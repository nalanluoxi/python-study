import json
import threading
import time
from pathlib import Path


VALID_MSG_TYPES = {
    "message",
    "broadcast",
    "shutdown_request",         # 队长 -> 成员：请求关闭
    "shutdown_response",        # 成员 -> 队长：回复是否同意关闭
    "plan_approval_response",   # 队长 -> 成员：回复计划是否批准
}


class MessageBus:
    """
    文件型消息总线，每个成员独占一个 JSONL 文件作为邮箱。

    目录结构（index_dir = WORKDIR/.bus/）：
        .bus/
        ├── lead.jsonl        ← 队长邮箱（成员 -> 队长 的消息写这里）
        ├── alice.jsonl       ← 成员 alice 的邮箱
        └── bob.jsonl         ← 成员 bob 的邮箱

    重要：MyAiClient.py 中 BUS 和 TEAM 必须使用同一个 index_dir，
          否则队长和成员会读写不同目录，消息无法互达。
    """

    index_dir: Path
    _tracker_lock: threading.Lock
    shutdown_requests: dict   # { request_id: {"target": 成员名, "status": "pending|approved|rejected"} }
    plan_requests: dict       # { request_id: {"from": 成员名, "plan": 计划文本, "status": "pending|..."} }

    def __init__(self, index_dir: Path):
        self.index_dir = index_dir   # 通常为 WORKDIR/.bus/
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self._tracker_lock = threading.Lock()
        self.shutdown_requests = {}
        self.plan_requests = {}

    def send(self, sender: str, to: str, content: str,
             msg_type: str = "message", extra: dict = None) -> str:
        """追加一条消息到收件人邮箱：index_dir/{to}.jsonl"""
        if msg_type not in VALID_MSG_TYPES:
            return f"Error: 不支持的消息类型 '{msg_type}'. 支持类型有: {VALID_MSG_TYPES}"
        msg = {
            "type": msg_type,
            "from": sender,
            "content": content,
            "timestamp": time.time(),
        }
        if extra:
            msg.update(extra)
        inbox_path = self.index_dir / f"{to}.jsonl"  # 收件人邮箱文件
        with open(inbox_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(msg, ensure_ascii=False) + "\n")
        return f"发送 {msg_type} 给 {to}"

    def read_inbox(self, name: str) -> list:
        """读取并清空邮箱（drain 模式）：index_dir/{name}.jsonl"""
        index_path = self.index_dir / f"{name}.jsonl"  # 读取者自己的邮箱文件
        if not index_path.exists():
            return []
        messages = []
        for line in index_path.read_text(encoding="utf-8").strip().splitlines():
            if line:
                messages.append(json.loads(line))
        index_path.write_text("")  # 读后清空，防止重复处理
        return messages

    def broadcast(self, sender: str, content: str, teammates: list) -> str:
        for name in teammates:
            if name != sender:
                self.send(sender, name, content, "broadcast")
        return f"广播给 {len(teammates)} 个成员"