

import os
import subprocess
from pathlib import Path
import TodoManager

import SkillLoader

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

WORKDIR = Path.cwd()
client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.environ["MODEL_ID"]
ToDo=TodoManager.TodoManager ()
SKILLS_DIR = (WORKDIR / "skill").resolve()
SkillLoader = SkillLoader.SkillLoader(SKILLS_DIR)

SYSTEM = f"""你叫北风，你是一个coding ai，在工作目录为 {WORKDIR}. 使用工具去解决问题.
使用待办工具来规划多步骤任务。在开始前标记为进行中，完成后标记为已完成。优先使用工具而不是文字描述
你还可以加载skill来处理特殊的业务需求 你可以获取的skill有:{SkillLoader.get_skillName()}
"""

SUBAGENT_SYSTEM = f"""你叫一筒，你是一个coding ai，是工作目录为 {WORKDIR}编码子代理。完成所给任务，然后总结你的发现。使用工具去解决问题.
使用待办工具来规划多步骤任务。在开始前标记为进行中，完成后标记为已完成。优先使用工具而不是文字描述"""



# -- The dispatch map: {tool_name: handler} --




NOMAL_TOOL_HANDLERS = {
    "bash":       lambda **kw: run_bash(kw["command"]),
    "read_file":  lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":  lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
    "todo_tool":  lambda **kw: ToDo.update(kw["items"]),
    "load_skill": lambda **kw: SkillLoader.get_content(kw["name"]),
}

PAREMENT_TOOL_HANDLERS = {
    **NOMAL_TOOL_HANDLERS,
    "build_child_task" : lambda **kw: run_subagent(kw["prompt"])
}



NOMAL_TOOLS = [
    {"name": "bash", "description": "运行终端命令",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "读取文件",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}},
    {
        "name": "write_file",
        "description": "写文件",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "edit_file",
        "description": "精确替换文件里的文本内容",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string"
                },
                "old_text": {
                    "type": "string"
                },
                "new_text": {
                    "type": "string"
                }
            },
            "required": ["path", "old_text", "new_text"]
        }
    },
    {
        "name": "todo_tool",
        "description": "更新任务列表。跟踪多步骤任务的进展。",
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "string"
                            },
                            "text": {
                                "type": "string"
                            },
                            "status": {
                                "type": "string",
                                "enum": ["pending", "in_progress", "completed"]
                            }
                        }
                    }
                }
            },
            "required": ["items"]
        }
    },
    {
        "name": "load_skill",
        "description": "通过名字加载skill",
        "input_schema": {
             "type": "object",
             "properties": {
                 "name": {
                     "type": "string",
                     "description": "skill名字，用来加载对应skill"}
             },
             "required": ["name"]
         }
    },
]

PARENT_TOOLS = NOMAL_TOOLS + [
    {
        "name": "build_child_task",
        "description": "生成一个具有新上下文的子代理，进行执行任务",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string"}
            },
            "required": ["prompt",]
        }
    },
]

def run_subagent(prompt: str) -> str:
    sub_messages = [{"role": "user", "content": prompt}]
    for _ in range(30):  # safety limit
        response = client.messages.create(
            model=MODEL, system=SUBAGENT_SYSTEM,
            messages=sub_messages,
            tools=NOMAL_TOOLS, max_tokens=8000,
        )
        sub_messages.append({"role": "assistant",
                             "content": response.content})
        if response.stop_reason != "tool_use":
            break
        results = []
        for block in response.content:
            if block.type == "tool_use":
                handler = NOMAL_TOOL_HANDLERS.get(block.name)
                output = handler(**block.input)
                results.append({"type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(output)[:50000]})
        sub_messages.append({"role": "user", "content": results})
    return "".join(
        b.text for b in response.content if hasattr(b, "text")
    ) or "(no summary)"

def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    print(f"路径检查 :{path}")
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path

def run_bash(command: str) -> str:
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(command, shell=True, cwd=WORKDIR,
                           capture_output=True, text=True, timeout=120,
                           encoding='utf-8', errors='replace')
        stdout = r.stdout if r.stdout else ""
        stderr = r.stderr if r.stderr else ""
        out = (stdout + stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"
    except Exception as e:
        return f"Error: {str(e)}"
#def run_bash(command: str) -> str:
#    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
#    if any(d in command for d in dangerous):
#        return "Error: Dangerous command blocked"
#    try:
#        r = subprocess.run(command, shell=True, cwd=WORKDIR,
#                           capture_output=True, text=True, timeout=120)
#        out = (r.stdout + r.stderr).strip()
#        return out[:50000] if out else "(no output)"
#    except subprocess.TimeoutExpired:
#        return "Error: Timeout (120s)"


def run_read(path: str, limit: int = None) -> str:
    try:
        text = safe_path(path).read_text()
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        content = fp.read_text()
        if old_text not in content:
            return f"Error: Text not found in {path}"
        fp.write_text(content.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"




def agent_main(messagelist):
    while True:
        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messagelist,
            tools=PARENT_TOOLS, max_tokens=8000,
        )
        messagelist.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return
        results = []
        todo_used=False
        for block in response.content:
            if block.type == "tool_use":
                handler = PAREMENT_TOOL_HANDLERS.get(block.name)
                output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                print(f"> {block.name}:")
                print(output[:200])
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
                if block.name=="todo_tool":
                    todo_used=True

        #todo_need_count=0 if todo_used else todo_need_count+1
        #if todo_need_count > 3:
        #    print("需要调用todo工具进行规划")
        #    results.append({"type": "text", "text": "<reminder>更新todo.</reminder>"})
        messagelist.append({"role": "user", "content": results})


if __name__ == '__main__':
    #print(SYSTEM)
    print('\033[32m北风|>>你好我叫北风\033[32m')
    history=[]
    while True:
        try:
            user_input = input("\033[33m用户|>>\033[33m")
        except EOFError:
            print(f'\033[32m北风|>>出现错误  {EOFError}\033[32m')
            break
        if user_input.strip().lower() in ('q',"","exit"):
            print("\033[32m北风|>>Bye2!\033[32m")
            break
        history.append({"role": "user", "content": user_input})
        agent_main(history)
        response_content= history[-1]["content"]
        if isinstance(response_content, list):
            for item in response_content:
                if hasattr(item, "text"):
                    print("\033[32m北风|>>", item.text)
        print()
