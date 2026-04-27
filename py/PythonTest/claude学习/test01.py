
from pathlib import Path

WORKDIR = Path.cwd()

def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    print(WORKDIR)
    print(f"路径检查 :{path}")
   #if not path.is_relative_to(WORKDIR):
   #    raise ValueError(f"Path escapes workspace: {p}")
    return path
#D:\python_project\pystu\py\PythonTest\python基础\NumPy学习

if __name__ == '__main__':
    print(safe_path("../python基础/NumPy学习/test999.py"))