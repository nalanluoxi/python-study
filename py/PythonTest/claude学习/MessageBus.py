import json
import time
from pathlib import Path


VALID_MSG_TYPES = {
    "message",
    "broadcast",
    "shutdown_request",
    "shutdown_response",
    "plan_approval_response",
}


class MessageBus:

    index_dir: Path

    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def send(self, sender: str, to: str, content: str,
             msg_type: str = "message", extra: dict = None) -> str:
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
        inbox_path = self.index_dir / f"{to}.jsonl"
        with open(inbox_path, "a") as f:
            f.write(json.dumps(msg) + "\n")
        return f"发送 {msg_type} 给 {to}"

    def read_inbox(self, name: str) -> list:
        index_path = self.index_dir / f"{name}.jsonl"
        if not index_path.exists():
            return []
        messages = []
        for line in index_path.read_text().strip().splitlines():
            if line:
                messages.append(json.loads(line))
        index_path.write_text("")  # 读后清空（drain）
        return json.dumps(messages, indent=2)

    def broadcast(self, sender: str, content: str, teammates: list) -> str:
        for name in teammates:
            if name != sender:
                self.send(sender, name, content, "broadcast")
        return f"广播给 {len(teammates)} 个成员"