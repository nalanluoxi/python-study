
VALID_MSG_TYPES = {
    "message",
    "broadcast",
    "shutdown_request",         # 队长 -> 成员：请求关闭
    "shutdown_response",        # 成员 -> 队长：回复是否同意关闭
    "plan_approval_response",   # 队长 -> 成员：回复计划是否批准
}
NOMAL_TOOLS = [
    {
        "name": "bash",
        "description": "运行终端命令",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "读取文件",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string"
                },
                "limit": {
                    "type": "integer"
                }
            },
            "required": ["path"]
        }
    },
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
    {
        "name": "compact",
        "description": "手动对内容进行压缩",
        "input_schema": {
            "type": "object",
            "properties": {
                "focus": {
                    "type": "string",
                    "description": "摘要中应保留哪些内容"}
            },
            "required": []
        }
    },
    {
        "name": "task_create",
        "description": "创建一个新的任务",
        "input_schema": {
            "type": "object",
            "properties": {
                "subject": {
                    "type": "string"
                },
                "description": {
                    "type": "string"
                }
            },
            "required": ["subject"]
        }
    },
    {
        "name": "task_update",
        "description": "更新修改任务,更新任务状态或依赖项。",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed"]
                },
                "add_blocked_by": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    }
                },
                "remove_blocked_by": {
                    "type": "array",
                    "items": {
                        "type": "integer"
                    }
                }
            },
            "required": ["task_id"]
        }
    },

    {
        "name": "task_get",
        "description": "通过任务 ID 获取任务的完整详细信息。",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "task_get_all",
        "description": "列出所有任务及状态摘要。",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "background_run",
        "description": "在后台线程中运行命令。立即返回 task_id。",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "check_background",
        "description": "检查由 background_run 启动的 shell 命令的执行状态。task_id 是 background_run 返回的 8 位随机字符串（如 'a3f9b2c1'），不是成员名称。省略 task_id 可列出所有后台 shell 任务。",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"}
            }
        }
    },
    {
        "name": "worktree_create",
        "description": "创建 git worktree，可选绑定到指定任务。",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},        # worktree 名称（同时作为目录名和分支名后缀）
                "task_id": {"type": "integer"},    # 可选：关联的任务 ID
                "base_ref": {"type": "string"},    # 可选：基于哪个分支/提交创建（默认 HEAD）
            },
            "required": ["name"],
        },
    },
    {
        "name": "worktree_list",
        "description": "列出 .worktrees/index.json 中跟踪的所有 worktree。",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "worktree_status",
        "description": "查看指定 worktree 的 git 状态（文件变更情况）。",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    {
        "name": "worktree_run",
        "description": "在指定 worktree 目录中执行 shell 命令（适合构建、测试等任务）。",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "command": {"type": "string"},
            },
            "required": ["name", "command"],
        },
    },
    {
        "name": "worktree_remove",
        "description": "删除 worktree，可选同时将关联任务标记为已完成。",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "force": {"type": "boolean"},        # 可选：强制删除（即使有未提交修改）
                "complete_task": {"type": "boolean"},# 可选：同时完成关联任务
            },
            "required": ["name"],
        },
    },
    {
        "name": "worktree_keep",
        "description": "将 worktree 标记为保留状态（不删除目录，只更新索引状态）。",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    },
    # ── 事件查询工具 ──────────────────────────────────────────────────────────
    {
        "name": "worktree_events",
        "description": "查看 .worktrees/events.jsonl 中最近的 worktree/任务生命周期事件。",
        "input_schema": {
            "type": "object",
            "properties": {"limit": {"type": "integer"}},  # 可选：返回最近多少条记录
        },
    },

]

TEAMMATE_TOOLS = NOMAL_TOOLS + [
    {
        "name": "send_message",
        "description": "发送一个消息给团队的其他成员",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "content": {"type": "string"},
                "msg_type": {"type": "string", "enum": list(VALID_MSG_TYPES)}},
            "required": ["to", "content"]
        }
    },
    {
        "name": "read_inbox",
        "description": "阅读并清理你的收件箱.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "shutdown_response",
        "description": "响应队长的关闭请求，确认或拒绝关闭。",
        "input_schema": {
            "type": "object",
            "properties": {
                "request_id": {"type": "string"},
                "approve": {"type": "boolean"},
                "reason": {"type": "string"}
            },
            "required": ["request_id", "approve"]
        }
    },
    {
        "name": "plan_approval",
        "description": "向队长提交工作计划，等待审批后再执行重要操作。",
        "input_schema": {
            "type": "object",
            "properties": {
                "plan": {"type": "string", "description": "要提交审批的计划内容"}
            },
            "required": ["plan"]
        }
    },
    {
        "name": "task_claim",
        "description": "从任务看板认领一个待处理任务，认领后状态变为 in_progress。task_id 是任务的整数编号。",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "要认领的任务 ID"}
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "idle",
        "description": "Signal that you have no more work. Enters idle polling phase.",
        "input_schema": {
            "type": "object", "properties": {}
        }
    },

]

PARENT_TOOLS = NOMAL_TOOLS + [
    {
        "name": "build_child_task",
        "description": "派生一个独立子代理执行单一任务，子代理有全新上下文。prompt 字段填写要执行的具体任务描述，不是任务ID。",
        "input_schema": {
            "type": "object",
            "properties": {"prompt": {"type": "string", "description": "要执行的具体任务描述（自然语言），不是任务ID"}},
            "required": ["prompt"]
        }
    },
    {
        "name": "send_message",
        "description": "向团队成员发送消息",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "content": {"type": "string"},
                "msg_type": {"type": "string", "enum": list(VALID_MSG_TYPES)}},
            "required": ["to", "content"]
        }
    },
    {
        "name": "read_inbox",
        "description": "阅读并清理你的收件箱。系统会自动注入新消息，无需主动轮询。只在需要查看当前未读消息时调用一次。",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "shutdown_request",
        "description": "请求队友正常关闭进程。返回一个用于跟踪的请求 ID。",
        "input_schema": {
            "type": "object",
            "properties": {"teammate": {"type": "string"}},
            "required": ["teammate"]
        }
    },
    {
        "name": "plan_approval",
        "description": "批准或拒绝队友的计划。提供请求 ID + 批准 + 可选反馈。",
        "input_schema": {
            "type": "object",
            "properties": {
                "request_id": {"type": "string"},
                "approve": {"type": "boolean"},
                "feedback": {"type": "string"}
            },
            "required": ["request_id", "approve"]
        }
    },
    {
        "name": "spawn_teammate",
        "description": "派生一个新的团队成员，在独立线程中运行。",
        "input_schema": {
            "type": "object",
            "properties": {
                "name":   {"type": "string", "description": "成员名称"},
                "role":   {"type": "string", "description": "成员角色"},
                "prompt": {"type": "string", "description": "分配给成员的初始任务"}
            },
            "required": ["name", "role", "prompt"]
        }
    },
    {
        "name": "list_teammates",
        "description": "列出所有团队成员及其当前角色和状态（working/idle/shutdown）。注意：成员完成任务后会主动发消息到你的收件箱，不要反复轮询此工具等待状态变化，应改用 read_inbox 等待通知。",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
]