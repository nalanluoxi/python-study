
from typing import TypedDict, Literal

TodoStatus = Literal["pending", "in_progress", "completed"]

VALID_STATUSES: tuple[TodoStatus, ...] = ("pending", "in_progress", "completed")
MAX_TODOS: int = 20
STATUS_MARKERS: dict[TodoStatus, str] = {
    "pending": "[ ]",
    "in_progress": "[>]",
    "completed": "[v]",
}


class TodoItem(TypedDict):
    id: str
    text: str
    status: TodoStatus


class TodoManager:
    items: list[TodoItem]

    def __init__(self) -> None:
        self.items = []

    def update(self, items: list[dict]) -> str:
        if len(items) > MAX_TODOS:
            raise ValueError(f"Max {MAX_TODOS} todos allowed")
        validated: list[TodoItem] = []
        in_progress_count: int = 0
        for i, item in enumerate(items):
            text: str = str(item.get("text", "")).strip()
            status: str = str(item.get("status", "pending")).lower()
            item_id: str = str(item.get("id", str(i + 1)))
            if not text:
                raise ValueError(f"Item {item_id}: text required")
            if status not in VALID_STATUSES:
                raise ValueError(f"Item {item_id}: invalid status '{status}'")
            if status == "in_progress":
                in_progress_count += 1
            validated.append({"id": item_id, "text": text, "status": status})  # type: ignore[typeddict-item]
        if in_progress_count > 1:
            raise ValueError("Only one task can be in_progress at a time")
        self.items = validated
        return self.render()

    def render(self) -> str:
        if not self.items:
            return "No todos."
        lines: list[str] = []
        for item in self.items:
            marker: str = STATUS_MARKERS[item["status"]]
            lines.append(f"{marker} #{item['id']}: {item['text']}")
        done: int = sum(1 for t in self.items if t["status"] == "completed")
        lines.append(f"\n({done}/{len(self.items)} completed)")
        return "\n".join(lines)