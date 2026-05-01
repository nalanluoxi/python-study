import threading
import subprocess
import uuid
from pathlib import Path

class BackGroundManager:

    def __init__(self, workdir: Path):
        self.tasks={}
        self._notification_queue=[]
        self._lock=threading.Lock()
        self.WORKDIR=workdir

    def run(self, command: str) -> str:
        """启动一个后台线程，立即返回 task_id，不等待命令执行完毕。"""
        task_id = str(uuid.uuid4())[:8]  # 生成8位随机唯一ID，作为任务标识
        self.tasks[task_id] = {"status": "running", "result": None, "command": command}
        thread = threading.Thread(
            target=self._execute, args=(task_id, command), daemon=True
            # daemon=True：守护线程，主程序退出时此线程自动销毁
        )
        thread.start()  # 启动线程，立即返回，不阻塞主线程
        return f"后台线程 {task_id} 开始运行: {command[:80]}"


    def _execute(self,task_id:str,command:str):
        try:
            r = subprocess.run(
                command, shell=True, cwd=self.WORKDIR,
                capture_output=True, text=True, timeout=300  # 最多等待300秒
            )
            output = (r.stdout + r.stderr).strip()[:50000]  # 合并标准输出和错误输出，限制50000字符
            status = "completed"
        except subprocess.TimeoutExpired:
            output = "Error: Timeout (300s)"
            status = "timeout"
        except Exception as e:
            output = f"Error: {e}"
            status = "error"
        self.tasks[task_id]["status"]=status
        self.tasks[task_id]["result"]=output
        with self._lock:
            self._notification_queue.append({
                "task_id":task_id,
                "status":status,
                "command":command,
                "result":(output or "(没有输出)")[:500],
            })

    def check(self, task_id: str = None) -> str:
        """查询单个任务状态，不传 task_id 则列出所有任务。"""
        if task_id:
            t = self.tasks.get(task_id)
            if not t:
                return f"Error: Unknown task {task_id}"
            return f"[{t['status']}] {t['command'][:60]}\n{t.get('result') or '(running)'}"
        lines = []
        for tid, t in self.tasks.items():
            lines.append(f"{tid}: [{t['status']}] {t['command'][:60]}")
        return "\n".join(lines) if lines else "No background tasks."

    def drain_notifications(self) -> list:
        """取出并清空所有待处理的完成通知（每次 LLM 调用前调用此方法）。"""
        with self._lock:  # 加锁，防止在读取同时后台线程又在写入
            notifs = list(self._notification_queue)  # 复制一份
            self._notification_queue.clear()          # 清空原队列
        return notifs


