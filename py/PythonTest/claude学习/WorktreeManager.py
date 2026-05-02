import json
import re
import subprocess
import time
from pathlib import Path


def detect_repo_root(start: Path):
    """从 start 目录向上查找 .git，返回仓库根目录；找不到则返回 None。"""
    current = start.resolve()
    for _ in range(20):
        if (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


class WorktreeManager:
    def __init__(self, repo_root: Path, tasks, events):
        """
        初始化工作树管理器。
        repo_root: git 仓库根目录
        tasks: 任务管理器实例（用于创建/删除 worktree 时同步更新任务状态）
        events: 事件总线实例（用于记录生命周期事件）
        """
        self.repo_root = repo_root
        self.tasks = tasks
        self.events = events
        self.dir = repo_root / ".worktrees"          # 所有 worktree 的父目录
        self.dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.dir / "index.json"    # 索引文件，记录所有 worktree 的元数据
        if not self.index_path.exists():
            # 初始化空的索引文件
            self.index_path.write_text(json.dumps({"worktrees": []}, indent=2))
        self.git_available = self._is_git_repo()


    def _is_git_repo(self) -> bool:
        """
        检测当前目录是否在 git 仓库内。
        git worktree 功能依赖 git，非 git 仓库无法使用。
        """
        try:
            r = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return r.returncode == 0  # 返回码 0 表示在 git 仓库内
        except Exception:
            return False

    def _run_git(self, args: list[str]) -> str:
        """
        执行 git 命令的通用方法。
        args: git 命令的参数列表（不含 "git" 本身），如 ["worktree", "add", ...]
        命令失败时抛出 RuntimeError，包含 git 的错误信息。
        """
        if not self.git_available:
            raise RuntimeError("Not in a git repository. worktree tools require git.")
        r = subprocess.run(
            ["git", *args],   # *args 是解包操作，相当于把列表展开为单独的参数
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=120,  # git 操作最多等待 120 秒（大仓库可能需要时间）
        )
        if r.returncode != 0:
            msg = (r.stdout + r.stderr).strip()
            raise RuntimeError(msg or f"git {' '.join(args)} failed")
        return (r.stdout + r.stderr).strip() or "(no output)"

    def _load_index(self) -> dict:
        """从磁盘加载 worktree 索引文件。"""
        return json.loads(self.index_path.read_text())

    def _save_index(self, data: dict):
        """将 worktree 索引保存回磁盘。"""
        self.index_path.write_text(json.dumps(data, indent=2))

    def _find(self, name: str) -> dict :
        """在索引中按名称查找 worktree，找不到返回 None。"""
        idx = self._load_index()
        for wt in idx.get("worktrees", []):
            if wt.get("name") == name:
                return wt
        return None

    def _validate_name(self, name: str):
        """
        验证 worktree 名称格式：只允许字母、数字、点、下划线、连字符，长度 1-40。
        这样可以安全地作为目录名和 git 分支名使用，避免特殊字符导致的问题。
        re.fullmatch 表示整个字符串都必须匹配该模式（不能有多余字符）。
        """
        if not re.fullmatch(r"[A-Za-z0-9._-]{1,40}", name or ""):
            raise ValueError(
                "无效的 worktree 名称。只允许使用 1-40 个字符：字母、数字、.、_、-"
            )

    def create(self, name: str, task_id: int = None, base_ref: str = "HEAD") -> str:
        """
        创建一个新的 git worktree，并可选绑定到指定任务。
        name: worktree 名称（同时作为目录名和分支名后缀）
        task_id: 可选，关联的任务 ID
        base_ref: 基于哪个 git 引用创建（默认 HEAD，即当前最新提交）

        流程：
        1. 验证名称 → 2. 发送"创建前"事件 → 3. 执行 git 命令 →
        4. 更新索引 → 5. 绑定任务（如有）→ 6. 发送"创建后"事件
        """
        self._validate_name(name)
        if self._find(name):
            raise ValueError(f"Worktree '{name}' 已存在于索引中")
        if task_id is not None and not self.tasks.exists(task_id):
            raise ValueError(f"Task {task_id} not found")

        path = self.dir / name         # worktree 目录路径：.worktrees/name/
        branch = f"wt/{name}"          # 对应的 git 分支名：wt/name
        # 记录"即将创建"事件（用于审计：即使后续失败也有记录）
        self.events.emit(
            "worktree.create.before",
            task={"id": task_id} if task_id is not None else {},
            worktree={"name": name, "base_ref": base_ref},
        )
        try:
            # 执行 git worktree add -b wt/name .worktrees/name HEAD
            # -b branch: 同时创建新分支
            self._run_git(["worktree", "add", "-b", branch, str(path), base_ref])

            # 构建索引条目
            entry = {
                "name": name,
                "path": str(path),
                "branch": branch,
                "task_id": task_id,
                "status": "active",
                "created_at": time.time(),
            }

            # 更新索引文件（追加新条目）
            idx = self._load_index()
            idx["worktrees"].append(entry)
            self._save_index(idx)

            # 如果指定了任务 ID，则将任务与此 worktree 绑定
            if task_id is not None:
                self.tasks.bind_worktree(task_id, name)

            # 记录"创建成功"事件
            self.events.emit(
                "worktree.create.after",
                task={"id": task_id} if task_id is not None else {},
                worktree={
                    "name": name,
                    "path": str(path),
                    "branch": branch,
                    "status": "active",
                },
            )
            return json.dumps(entry, indent=2)
        except Exception as e:
            # 记录"创建失败"事件（包含错误信息）
            self.events.emit(
                "worktree.create.failed",
                task={"id": task_id} if task_id is not None else {},
                worktree={"name": name, "base_ref": base_ref},
                error=str(e),
            )
            raise  # 重新抛出异常，让调用方知道创建失败

    def list_all(self) -> str:
        """列出索引中所有 worktree 的状态信息。"""
        idx = self._load_index()
        wts = idx.get("worktrees", [])
        if not wts:
            return "No worktrees in index."
        lines = []
        for wt in wts:
            suffix = f" task={wt['task_id']}" if wt.get("task_id") else ""
            # 格式：[状态] 名称 -> 路径 (分支名) task=任务ID
            lines.append(
                f"[{wt.get('status', 'unknown')}] {wt['name']} -> "
                f"{wt['path']} ({wt.get('branch', '-')}){suffix}"
            )
        return "\n".join(lines)

    def status(self, name: str) -> str:
        """
        查询指定 worktree 的 git 状态（类似在该目录执行 git status）。
        --short: 简短格式（文件列表）
        --branch: 同时显示分支信息
        """
        wt = self._find(name)
        if not wt:
            return f"Error: Unknown worktree '{name}'"
        path = Path(wt["path"])
        if not path.exists():
            return f"Error: Worktree path missing: {path}"
        r = subprocess.run(
            ["git", "status", "--short", "--branch"],
            cwd=path,          # 注意：在 worktree 目录下执行，而非仓库根目录
            capture_output=True,
            text=True,
            timeout=60,
        )
        text = (r.stdout + r.stderr).strip()
        return text or "Clean worktree"  # 无输出则表示工作区干净

    def run(self, name: str, command: str) -> str:
        """
        在指定 worktree 目录中执行 shell 命令。
        与 run_bash() 的区别：这里的工作目录是 worktree 目录，而非主工作区。
        超时时间为 300 秒（允许执行耗时较长的构建命令）。
        """
        # 危险命令黑名单（防止 AI 执行破坏性操作）
        dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
        if any(d in command for d in dangerous):
            return "Error: Dangerous command blocked"

        wt = self._find(name)
        if not wt:
            return f"Error: Unknown worktree '{name}'"
        path = Path(wt["path"])
        if not path.exists():
            return f"Error: Worktree path missing: {path}"

        try:
            r = subprocess.run(
                command,
                shell=True,    # shell=True：通过 shell 执行（支持管道、重定向等）
                cwd=path,      # 在 worktree 目录下执行命令
                capture_output=True,
                text=True,
                timeout=300,   # 比普通 bash 多一倍时间，适合构建任务
            )
            out = (r.stdout + r.stderr).strip()
            return out[:50000] if out else "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Timeout (300s)"

    def remove(self, name: str, force: bool = False, complete_task: bool = False) -> str:
        """
        删除指定的 worktree。
        force: 是否强制删除（即使有未提交的修改）
        complete_task: 是否同时将关联任务标记为已完成（"删除工作间"等于"任务完工"）

        流程：发事件 → git 删除 → 可选完成任务 → 更新索引 → 发事件
        """
        wt = self._find(name)
        if not wt:
            return f"Error: Unknown worktree '{name}'"

        # 记录"即将删除"事件
        self.events.emit(
            "worktree.remove.before",
            task={"id": wt.get("task_id")} if wt.get("task_id") is not None else {},
            worktree={"name": name, "path": wt.get("path")},
        )
        try:
            # 构建 git worktree remove [--force] <path> 命令
            args = ["worktree", "remove"]
            if force:
                args.append("--force")  # 强制删除（放弃未提交的修改）
            args.append(wt["path"])
            self._run_git(args)

            # 如果设置了 complete_task=True 且任务存在，则同步完成任务
            if complete_task and wt.get("task_id") is not None:
                task_id = wt["task_id"]
                before = json.loads(self.tasks.get(task_id))  # 记录完成前的状态（用于事件）
                self.tasks.update(task_id, status="completed")
                self.tasks.unbind_worktree(task_id)  # 解除 worktree 绑定
                self.events.emit(
                    "task.completed",
                    task={
                        "id": task_id,
                        "subject": before.get("subject", ""),
                        "status": "completed",
                    },
                    worktree={"name": name},
                )

            # 更新索引：把 worktree 状态改为 removed（保留历史记录，不从索引中删除）
            idx = self._load_index()
            for item in idx.get("worktrees", []):
                if item.get("name") == name:
                    item["status"] = "removed"
                    item["removed_at"] = time.time()
            self._save_index(idx)

            # 记录"删除成功"事件
            self.events.emit(
                "worktree.remove.after",
                task={"id": wt.get("task_id")} if wt.get("task_id") is not None else {},
                worktree={"name": name, "path": wt.get("path"), "status": "removed"},
            )
            return f"Removed worktree '{name}'"
        except Exception as e:
            # 记录"删除失败"事件
            self.events.emit(
                "worktree.remove.failed",
                task={"id": wt.get("task_id")} if wt.get("task_id") is not None else {},
                worktree={"name": name, "path": wt.get("path")},
                error=str(e),
            )
            raise

    def keep(self, name: str) -> str:
        """
        将 worktree 标记为"保留"状态（kept）。
        与 remove 的区别：不删除目录和分支，只在索引中改状态。
        使用场景：任务完成后想保留代码变更供后续 review 或合并。
        """
        wt = self._find(name)
        if not wt:
            return f"Error: Unknown worktree '{name}'"

        idx = self._load_index()
        kept = None
        for item in idx.get("worktrees", []):
            if item.get("name") == name:
                item["status"] = "kept"
                item["kept_at"] = time.time()
                kept = item
        self._save_index(idx)

        # 记录"保留"事件
        self.events.emit(
            "worktree.keep",
            task={"id": wt.get("task_id")} if wt.get("task_id") is not None else {},
            worktree={
                "name": name,
                "path": wt.get("path"),
                "status": "kept",
            },
        )
        return json.dumps(kept, indent=2) if kept else f"Error: Unknown worktree '{name}'"

