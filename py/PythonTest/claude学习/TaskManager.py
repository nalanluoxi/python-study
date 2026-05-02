import json
import threading
import time
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
        self._claim_lock = threading.Lock()

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
            "id": self.next_task_id,
            "subject": subject,
            "description": description,
            "status": "pending",
            "blockedBy": [],
            "owner": "",
            "worktree": "",
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        self._save(task)
        self.next_task_id += 1
        return self._to_json(task)

    def exists(self,task_id:int) ->bool:
        return self._path(task_id).exists()


    def _path(self, task_id: int) -> Path:
        """根据任务 ID 生成对应的文件路径（如 .tasks/task_5.json）。"""
        return self.dir / f"task_{task_id}.json"

    def get(self, task_id: int) -> str:
        return self._to_json(self._load(task_id))

    def update(self, task_id: int, status: str = None, owner: str = None) -> str:

        task = self._load(task_id)
        if status:
            if status not in ("pending", "in_progress", "completed"):
                raise ValueError(f"Invalid status: {status}")
            task["status"] = status
        if owner is not None:
            task["owner"] = owner
        task["updated_at"] = time.time()
        self._save(task)
        return json.dumps(task, indent=2)


    def bind_worktree(self, task_id: int, worktree: str, owner: str = "") -> str:
        """
        将任务与一个 worktree 绑定（表示任务在该 worktree 中执行）。
        绑定后，如果任务还是 pending 状态，自动升级为 in_progress（进行中）。
        """
        task = self._load(task_id)
        task["worktree"] = worktree
        if owner:
            task["owner"] = owner
        if task["status"] == "pending":
            task["status"] = "in_progress"  # 一旦分配了执行环境，任务就变成"进行中"
        task["updated_at"] = time.time()
        self._save(task)
        return json.dumps(task, indent=2)

    def unbind_worktree(self, task_id: int) -> str:
        """解除任务与 worktree 的绑定（worktree 被删除时调用）。"""
        task = self._load(task_id)
        task["worktree"] = ""  # 清空 worktree 字段
        task["updated_at"] = time.time()
        self._save(task)
        return json.dumps(task, indent=2)

 #   def update(self, task_id: int, status: str = None,
 #              add_blocked_by: list = None, remove_blocked_by: list = None) -> str:
 #       task = self._load(task_id)
 #       if status:
 #           if status not in VALID_STATUSES:
 #               raise ValueError(f"不存在的状态: {status}")
 #           task["status"] = status
 #           if status == "completed":
 #               self._clear_dependency(task_id)
 #       if add_blocked_by:
 #           task["blockedBy"] = list(set(task["blockedBy"] + add_blocked_by))
 #       if remove_blocked_by:
 #           task["blockedBy"] = [i for i in task["blockedBy"] if i not in remove_blocked_by]
 #       self._save(task)
 #       return self._to_json(task)

    def _clear_dependency(self, completed_id: int):
        for f in self.dir.glob(FILE_PATTERN):
            task = json.loads(f.read_text())
            if completed_id in task.get("blockedBy", []):
                task["blockedBy"].remove(completed_id)
                self._save(task)

    def scan_unclaimed(self) -> list:
        """返回所有可认领的任务：pending、无 owner、无 blockedBy。"""
        result = []
        for f in sorted(self.dir.glob(FILE_PATTERN), key=lambda f: int(f.stem.split("_")[1])):
            task = json.loads(f.read_text())
            if (task.get("status") == "pending"
                    and not task.get("owner")
                    and not task.get("blockedBy")):
                result.append(task)
        return result

    def claim(self, task_id: int, owner: str) -> str:
        """认领任务：设置 owner 和状态为 in_progress。加锁防止多成员同时抢同一任务。"""
        with self._claim_lock:
            task = self._load(task_id)
            if task.get("owner"):
                return f"Error: 任务 {task_id} 已被 '{task['owner']}' 认领"
            if task.get("status") != "pending":
                return f"Error: 任务 {task_id} 状态为 '{task['status']}'，不可认领"
            if task.get("blockedBy"):
                return f"Error: 任务 {task_id} 有前置依赖未完成"
            task["owner"] = owner
            task["status"] = "in_progress"
            self._save(task)
            return self._to_json(task)

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