import platform
from typing import Any

from aura.tools.base import Tool
from aura.tools.models import ToolResult


class SystemInfoTool(Tool):
    @property
    def name(self) -> str:
        return "system_info"

    @property
    def description(self) -> str:
        return (
            "Returns basic information about "
            "the current operating system."
        )

    @property
    def category(self) -> str:
        return "system"

    @property
    def tags(self) -> list[str]:
        return [
            "system",
            "environment",
            "diagnostics",
        ]

    async def execute(
        self,
        **kwargs: Any,
    ) -> ToolResult:
        information = {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "python_version":
                platform.python_version(),
        }

        return ToolResult(
            success=True,
            output=information,
            metadata={
                "tool": self.name,
            },
        )