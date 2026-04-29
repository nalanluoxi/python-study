import json
from pathlib import Path

VALID_STATUSES = ("pending", "in_progress", "completed")
STATUS_MARKERS = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]"}
FILE_PATTERN = "task_*.json"
JSON_OPTS = {"indent": 2, "ensure_ascii": False}


class TaskManager:

    def __init__(self, tasks_dir: Path):
        self.dir = tasks_dir
        self.dir.mkdir(exist_ok=True)
        self.next_task_id = self._max_task_id() + 1

    def _max_task_id(self):
        ids = [int(f.stem.split("_")[1]) for f in self.dir.glob(FILE_PATTERN)]
        return max(ids) if ids else 0

    def _task_path(self, task_id: int) -> Path:
        return self.dir / f"task_{task_id}.json"

    def _load(self, task_id: int) -> dict:
        path = self._task_path(task_id)
        if not path.exists():
            raise ValueError(f"任务 {task_id} 没有被发现")
        return json.loads(path.read_text())

    def _save(self, task: dict):
        self._task_path(task["id"]).write_text(json.dumps(task, **JSON_OPTS))

    def _to_json(self, task: dict) -> str:
        return json.dumps(task, **JSON_OPTS)

    def create(self, subject: str, description: str = "") -> str:
        task = {
            "id": self.next_task_id, "subject": subject, "description": description,
            "status": "pending", "blockedBy": [], "owner": "",
        }
        self._save(task)
        self.next_task_id += 1
        return self._to_json(task)

    def get(self, task_id: int) -> str:
        return self._to_json(self._load(task_id))

    def update(self, task_id: int, status: str = None,
               add_blocked_by: list = None, remove_blocked_by: list = None) -> str:
        task = self._load(task_id)
        if status:
            if status not in VALID_STATUSES:
                raise ValueError(f"不存在的状态: {status}")
            task["status"] = status
            if status == "completed":
                self._clear_dependency(task_id)
        if add_blocked_by:
            task["blockedBy"] = list(set(task["blockedBy"] + add_blocked_by))
        if remove_blocked_by:
            task["blockedBy"] = [i for i in task["blockedBy"] if i not in remove_blocked_by]
        self._save(task)
        return self._to_json(task)

    def _clear_dependency(self, completed_id: int):
        for f in self.dir.glob(FILE_PATTERN):
            task = json.loads(f.read_text())
            if completed_id in task.get("blockedBy", []):
                task["blockedBy"].remove(completed_id)
                self._save(task)

    def list_all(self) -> str:
        files = sorted(self.dir.glob(FILE_PATTERN), key=lambda f: int(f.stem.split("_")[1]))
        tasks = [json.loads(f.read_text()) for f in files]
        if not tasks:
            return "No tasks."
        lines = []
        for t in tasks:
            marker = STATUS_MARKERS.get(t["status"], "[?]")
            blocked = f" (blocked by: {t['blockedBy']})" if t.get("blockedBy") else ""
            lines.append(f"{marker} #{t['id']}: {t['subject']}{blocked}")
        return "\n".join(lines)