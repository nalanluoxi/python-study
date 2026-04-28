# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概览

这是一个基于 Anthropic SDK 手动实现的 AI coding agent，通过 `ANTHROPIC_BASE_URL` 对接第三方兼容接口（当前为智谱 GLM）。

## 运行方式

```bash
# 激活虚拟环境（项目根目录 python-test/）
source ../../.venv/bin/activate

# 启动主 agent（交互式 CLI）
python MyAiClient.py

# 运行测试
python -m pytest tests/
# 或运行单个测试文件
python -m unittest tests/test_utils.py
```

## 环境变量（.env）

| 变量 | 说明 |
|------|------|
| `ANTHROPIC_API_KEY` | API Key（当前为智谱平台 key） |
| `ANTHROPIC_BASE_URL` | 第三方兼容接口地址，设置后会清除 `ANTHROPIC_AUTH_TOKEN` |
| `MODEL_ID` | 使用的模型名，如 `glm-4-flash` |

## 架构

### 核心文件

- **`MyAiClient.py`** — 主入口，包含两个 agent loop：
  - `agent_main()` — 父 agent，使用 `PARENT_TOOLS`，支持 `build_child_task` 派生子 agent
  - `run_subagent()` — 子 agent，使用 `NOMAL_TOOLS`，有独立上下文（30 轮安全限制）
- **`TOOL_package.py`** — 工具定义的独立包，`NOMAL_TOOLS` + `PARENT_TOOLS` 的 JSON schema
- **`SkillLoader.py`** — 从 `skill/` 目录递归加载 `SKILL.md` 文件，解析 YAML frontmatter
- **`TodoManager.py`** — 内存中的 todo 列表，限制最多 20 条、同时只能一条 `in_progress`

### 工具体系

父 agent 有两套工具：
- `NOMAL_TOOLS`：`bash`、`read_file`、`write_file`、`edit_file`、`todo_tool`、`load_skill`
- `PARENT_TOOLS`：在 `NOMAL_TOOLS` 基础上增加 `build_child_task`

`safe_path()` 对所有文件操作做路径校验，防止路径逃逸出 `WORKDIR`。

### Skill 系统

`skill/<name>/SKILL.md` 格式：
```
---
name: <skill名>
description: <描述>
tags: <可选标签>
---
<skill 正文内容>
```

`load_skill` 工具触发时，将正文以 `<skill name="...">...</skill>` 格式注入到 agent 上下文。

## 注意事项

- `MyAiClient.py` 中的工具定义与 `TOOL_package.py` 存在重复，两处需保持同步
- `compact` 工具在 `TOOL_package.py` 中有定义，但 `MyAiClient.py` 的 handler map 里尚未实现