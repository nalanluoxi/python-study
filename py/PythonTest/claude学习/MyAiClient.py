import os
import subprocess
from pathlib import Path
import TodoManager
import time
import json
import SkillLoader

from anthropic import Anthropic
from dotenv import load_dotenv

import TOOL_package

load_dotenv(override=True)

if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

WORKDIR = Path.cwd()

TRANSCRIPT_DIR = WORKDIR / ".transcripts"

client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.environ["MODEL_ID"]
ToDo = TodoManager.TodoManager()
SKILLS_DIR = (WORKDIR / "skill").resolve()
SkillLoader = SkillLoader.SkillLoader(SKILLS_DIR)

SYSTEM = f"""你叫北风，你是一个coding ai，在工作目录为 {WORKDIR}. 使用工具去解决问题.
使用待办工具来规划多步骤任务。在开始前标记为进行中，完成后标记为已完成。优先使用工具而不是文字描述
你还可以加载skill来处理特殊的业务需求 你可以获取的skill有:{SkillLoader.get_skillName()}
"""

SUBAGENT_SYSTEM = f"""你叫一筒，你是一个coding ai，是工作目录为 {WORKDIR}编码子代理。完成所给任务，然后总结你的发现。使用工具去解决问题.
使用待办工具来规划多步骤任务。在开始前标记为进行中，完成后标记为已完成。优先使用工具而不是文字描述"""

# -- The dispatch map: {tool_name: handler} --
KEEP_MAX_LEN = 3
MAX_TOKEN_LEN = 50000

NOMAL_TOOL_HANDLERS = {
    "bash": lambda **kw: run_bash(kw["command"]),
    "read_file": lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file": lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
    "todo_tool": lambda **kw: ToDo.update(kw["items"]),
    "load_skill": lambda **kw: SkillLoader.get_content(kw["name"]),
    "compact":    lambda **kw: "请求手动压缩",
}

PRESERVE_RESULT_TOOLS = {"read_file"}

PAREMENT_TOOL_HANDLERS = {
    **NOMAL_TOOL_HANDLERS,
    "build_child_task": lambda **kw: run_subagent(kw["prompt"])
}


def estimate_token(message: list) -> int:
    return len(str(message)) // 4 + 1


# 压缩message,替换为占位符
def micro_compact(message: list) -> list:
    tool_result = []
    for mesIndex, msg in enumerate(message):
        if msg["role"] == "user" and isinstance(msg["content"], list):
            for contIndex, data in enumerate(message["content"]):
                if isinstance(data, dict) and data.get("type") == "tool_result":
                    tool_result.append((mesIndex, contIndex, data))
    if len(tool_result) <= KEEP_MAX_LEN:
        return message
    tool_name_map = {}
    for msg in message:
        if msg["role"] == 'assistant':
            content = msg.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if hasattr(item, "type") and item.type == "tool_use":
                        tool_name_map[item.id] = item.name
    to_clear = tool_result[:-KEEP_MAX_LEN]
    for _, _, item in to_clear:
        if not isinstance(item.get("content"), list) or len(item.get("content")) <= 100:
            continue
        tool_use_id = item.get("tool_use_id", "")
        tool_name = tool_name_map.get(tool_use_id, "")
        if tool_name in PRESERVE_RESULT_TOOLS:
            continue
        item["content"] = f"[以前使用了工具:{tool_name}]"
    return message


def run_subagent(prompt: str) -> str:
    sub_messages = [{"role": "user", "content": prompt}]
    for _ in range(30):  # safety limit
        response = client.messages.create(
            model=MODEL, system=SUBAGENT_SYSTEM,
            messages=sub_messages,
            tools=TOOL_package.NOMAL_TOOLS, max_tokens=8000,
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


# def run_bash(command: str) -> str:
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


def auto_compressed(message: list):
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    transPath = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"
    with open(transPath, "w") as f:
        for msg in message:
            f.write(json.dumps(msg, default=str) + "\n")
    print(f"[历史保存到路径: {transPath}]")
    data = json.dumps(message, default=str)[-80000:]

    response = client.messages.create(model=MODEL,
                                      message=[{"role": "user", "content": """
                  为了保持对话的连贯性，请总结本次对话。内容包括：
                  1) 已完成的工作，2) 当前状况，3) 已做出的关键决策。
                  
                  下面是对话内容
                  """ + data}],
                                      max_tokens=2000,
                                      )
    summary=""
    for item in response.content:
        if hasattr(item,"test"):
            summary=item.text
            break
    if not summary:
        summary="未生成摘要"
    return [{"role": "user", "content": f"[对话内容精简版。文字稿: {transPath}]\n\n{summary}"}]

def agent_main(messagelist):
    while True:
        micro_compact(messagelist)
        if estimate_token(messagelist) > MAX_TOKEN_LEN:
            print("[需要进行压缩]")
            messagelist[:] = auto_compressed(messagelist)

        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messagelist,
            tools=TOOL_package.PARENT_TOOLS, max_tokens=8000,
        )
        messagelist.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            return
        results = []
        todo_used = False
        need_compress = False
        todo_need_count = 0
        for block in response.content:
            if block.type == "tool_use":
                if block.name == "compact":
                    need_compress = True
                    output = "压缩..."
                elif block.name == "todo_tool":
                    todo_used = True
                    handler = PAREMENT_TOOL_HANDLERS.get(block.name)
                    try:
                        output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                    except Exception as e:
                        output = f"Error: {e}"
                else:
                    handler = PAREMENT_TOOL_HANDLERS.get(block.name)
                    try:
                        output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                    except Exception as e:
                        output = f"Error: {e}"
                print(f"> {block.name}:")
                print(output[:200])
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": output})
        todo_need_count = 0 if todo_used else todo_need_count + 1
        if todo_need_count > 3:
            print("需要调用todo工具进行规划")
            results.append({"type": "text", "text": "<reminder>更新todo.</reminder>"})
        messagelist.append({"role": "user", "content": results})
        if need_compress:
            print("需要压缩")
            messagelist[:]= auto_compressed(messagelist)
            return


if __name__ == '__main__':
    # print(SYSTEM)
    print('\033[32m北风|>>你好我叫北风\033[32m')
    history = []
    while True:
        try:
            user_input = input("\033[33m用户|>>\033[33m")
        except EOFError:
            print(f'\033[32m北风|>>出现错误  {EOFError}\033[32m')
            break
        if user_input.strip().lower() in ('q', "", "exit"):
            print("\033[32m北风|>>Bye2!\033[32m")
            break
        history.append({"role": "user", "content": user_input})
        agent_main(history)
        response_content = history[-1]["content"]
        if isinstance(response_content, list):
            for item in response_content:
                if hasattr(item, "text"):
                    print("\033[32m北风|>>", item.text)
        print()
"""

帮我完成一个任务,首先第一步,创建一个文件夹,第二部创建一个hello.py文件,编写python代码输出helloworld!,第三创建一个data.txt文件,里面写上完整[测试文件],第四,创建一个文件step.txt,把你的所有过程计划记录下来.第五,创建一个子代理去扫描整个项目,创建一个projectall.txt,吧项目结构写入
"""