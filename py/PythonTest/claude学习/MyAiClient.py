import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

import TOOL_package
import SkillLoader as SkillLoaderModule
import TaskManager as TaskManagerModule
import TodoManager
from py.PythonTest.claude学习.BackgroudManager import BackGroundManager
from py.PythonTest.claude学习.MessageBus import MessageBus
from py.PythonTest.claude学习.TeammateManager import TeammateManager
from py.PythonTest.claude学习.ToolFunction import ToolFunction

# ── 环境初始化 ──────────────────────────────────────────────
load_dotenv(override=True)
if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

# ── 路径常量 ────────────────────────────────────────────────
WORKDIR = Path.cwd() / "work"
WORKDIR.mkdir(exist_ok=True)
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
TASKS_DIR = WORKDIR / ".tasks"
SKILLS_DIR = (WORKDIR / "../skill").resolve()

# ── 客户端 & 单例 ───────────────────────────────────────────
client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
MODEL = os.environ["MODEL_ID"]

ToDo = TodoManager.TodoManager()
skill_loader = SkillLoaderModule.SkillLoader(SKILLS_DIR)
task_manager = TaskManagerModule.TaskManager(TASKS_DIR)
BG_manager = BackGroundManager(WORKDIR)
# 队长邮箱目录：WORKDIR/.bus/lead.jsonl（必须与 TEAM 的 bus_dir 保持一致）
BUS = MessageBus(WORKDIR / ".bus")

# ── System Prompt ───────────────────────────────────────────
SYSTEM = f"""你叫北风，你是一个coding ai，是工作目录为 {WORKDIR}的团队负责人,需要负责管理团队成员，并遵守停机和计划审批流程.
同时需要使用工具去解决问题.
使用待办工具来规划多步骤任务。在开始前标记为进行中，完成后标记为已完成。优先使用工具而不是文字描述
你还可以加载skill来处理特殊的业务需求 你可以获取的skill有:{skill_loader.get_skillName()}"""

SUBAGENT_SYSTEM = f"""你叫一筒，你是一个coding ai，是工作目录为 {WORKDIR} 编码子代理。完成所给任务，然后总结你的发现。使用工具去解决问题.
使用待办工具来规划多步骤任务。在开始前标记为进行中，完成后标记为已完成。优先使用工具而不是文字描述
注意：此系统为 macOS，执行 Python 脚本须使用 python3 命令，不能使用 python。"""

MAX_TOKEN_LEN = 50_000

tool_function = ToolFunction(
    workdir=WORKDIR,
    todo=ToDo,
    skill_loader=skill_loader,
    task_manager=task_manager,
    bg_manager=BG_manager,
    client=client,
    model=MODEL,
    subagent_system=SUBAGENT_SYSTEM,
    nomal_tools=TOOL_package.NOMAL_TOOLS,
    transcript_dir=TRANSCRIPT_DIR,
)

TEAM = TeammateManager(
    team_dir=WORKDIR / ".team",       # 成员配置：WORKDIR/.team/config.json
    bus_dir=WORKDIR / ".bus",         # 消息总线目录（与上方 BUS 必须相同）：WORKDIR/.bus/{name}.jsonl
    client=client,
    model=MODEL,
    workdir=WORKDIR,
    tool_function=tool_function,
)
tool_function.set_team(TEAM)


# ── 父 Agent 主循环 ─────────────────────────────────────────
def agent_main(messagelist: list):
    todo_need_count = 0
    while True:
        # 读取队长邮箱（成员发来的 shutdown_response / plan_approval_response 等）
        # 邮箱文件：WORKDIR/.bus/lead.jsonl
        inbox = BUS.read_inbox("lead")
        if inbox:
            messagelist.append({"role": "user", "content": f"<inbox>{json.dumps(inbox, indent=2, ensure_ascii=False)}</inbox>"})
        notifs = BG_manager.drain_notifications()
        if notifs and messagelist:
            notif_text = "\n".join(
                f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs
            )
            messagelist.append({"role": "user", "content": f"<background-results>\n{notif_text}\n</background-results>"})
        tool_function.micro_compact(messagelist)
        if tool_function.estimate_token(messagelist) > MAX_TOKEN_LEN:
            print("[需要进行压缩]")
            messagelist[:] = tool_function.auto_compress(messagelist)

        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messagelist,
            tools=TOOL_package.PARENT_TOOLS, max_tokens=8000,
        )
        messagelist.append({"role": "assistant", "content": [b.model_dump() for b in response.content]})
        if response.stop_reason != "tool_use":
            return

        results = []
        todo_used = False
        need_compress = False

        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "compact":
                need_compress = True
                output = "压缩..."
            else:
                if block.name == "todo_tool":
                    todo_used = True
                try:
                    output = tool_function.dispatch_parent(block.name, block.input)
                except Exception as e:
                    output = f"Error: {e}"
            print(f"> {block.name}:\n{str(output)[:200]}")
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)})

        todo_need_count = 0 if todo_used else todo_need_count + 1
        messagelist.append({"role": "user", "content": results})
        if todo_need_count > 3:
            print("需要调用todo工具进行规划")
            messagelist.append({"role": "user", "content": "<reminder>请使用 todo_tool 更新任务进度。</reminder>"})
        if need_compress:
            print("需要压缩")
            messagelist[:] = tool_function.auto_compress(messagelist)
            return


# ── 入口 ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\033[32m北风|>> 你好我叫北风\033[0m")
    history = []
    try:
        while True:
            try:
                user_input = input("\033[33m用户|>> \033[0m")
            except EOFError:
                print(f"\033[32m北风|>> 出现错误 {EOFError}\033[0m")
                break
            if user_input.strip().lower() in ("q",  "exit"):
                print("\033[32m北风|>> Bye!\033[0m")
                break
            elif user_input.strip().lower() == "clear":
                history = []
                continue
            if user_input.strip() == "/team":
                print(TEAM.list_all())   # 查看团队成员状态
                continue
            if user_input.strip() == "/inbox":
                 print(json.dumps(BUS.read_inbox("lead"), indent=2))  # 查看队长邮箱
                 continue

            history.append({"role": "user", "content": user_input})
            agent_main(history)
            last = history[-1]["content"]
            if isinstance(last, list):
                for item in last:
                    if hasattr(item, "text"):
                        print(f"\033[32m北风|>> {item.text}\033[0m")
            print()
    except KeyboardInterrupt:
        print("\n\033[32m北风|>> Bye!\033[0m")