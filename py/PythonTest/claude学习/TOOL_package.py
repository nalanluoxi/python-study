from py.PythonTest.claude学习.MessageBus import MessageBus, VALID_MSG_TYPES

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
            "required": ["name"]
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
        "description": "检查后台任务状态。省略 task_id 可列出所有任务。",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"}
            }
        }
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
                "msg_type": {
                    "type": "string",
                    "enum": list(VALID_MSG_TYPES)}},
            "required": ["to", "content"]
        }
    },
    {
        "name": "read_inbox",
        "description": "阅读并清理你的收件箱.",
        "input_schema": {
            "type": "object", "properties": {}
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