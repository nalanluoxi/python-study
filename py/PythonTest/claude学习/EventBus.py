import json
import time
from pathlib import Path


class EventBus:
    def __init__(self,event_log_path:Path):
        self.path=event_log_path
        self.path.parent.mkdir(parents=True,exist_ok=True)
        if not  self.path.exists():
            self.path.write_text("")


    def emit(self, event: str, task: dict, worktree: dict, error: str = None):
        payload = {
            "event": event,
            "ts": time.time(),        # Unix 时间戳（自 1970 年起的秒数）
            "task": task or {},       # 如果 task 为 None，则用空字典代替
            "worktree": worktree or {},
        }
        if error:
            payload["error"] = error
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")



    def list_recent(self, limit: int = 20) -> str:
        n = max(1, min(int(limit or 20), 200))  # 限制在 [1, 200] 范围内
        lines = self.path.read_text(encoding="utf-8").splitlines()
        recent = lines[-n:]  # Python 切片：取最后 n 行
        items = []
        for line in recent:
            try:
                items.append(json.loads(line))  # 把每行 JSON 字符串解析为字典
            except Exception:
                items.append({"event": "parse_error", "raw": line})  # 解析失败时保留原始内容
        return json.dumps(items, indent=2)  # 返回格式化的 JSON 字符串







