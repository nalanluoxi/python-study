
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