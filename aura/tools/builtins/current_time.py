from datetime import UTC, datetime
from typing import Any

from aura.tools.base import Tool
from aura.tools.models import ToolResult


class CurrentTimeTool(Tool):
    @property
    def name(self) -> str:
        return "current_time"

    @property
    def description(self) -> str:
        return (
            "Returns the current UTC date and time."
        )

    @property
    def category(self) -> str:
        return "utility"

    @property
    def tags(self) -> list[str]:
        return [
            "time",
            "date",
            "clock",
            "utc",
        ]

    async def execute(
        self,
        **kwargs: Any,
    ) -> ToolResult:
        now = datetime.now(
            UTC
        )

        return ToolResult(
            success=True,
            output={
                "datetime": now.isoformat(),
                "date": now.date().isoformat(),
                "time": now.time().isoformat(),
                "timezone": "UTC",
            },
            metadata={
                "tool": self.name,
            },
        )