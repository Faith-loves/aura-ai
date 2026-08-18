from typing import Any

from aura.tools.base import Tool
from aura.tools.models import (
    ToolParameter,
    ToolParameterType,
    ToolResult,
)


class EchoTool(Tool):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return (
            "Returns the provided message."
        )

    @property
    def category(self) -> str:
        return "utility"

    @property
    def tags(self) -> list[str]:
        return [
            "echo",
            "utility",
            "testing",
        ]

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="message",
                description=(
                    "Message to return."
                ),
                parameter_type=(
                    ToolParameterType.STRING
                ),
                required=True,
            )
        ]

    async def execute(
        self,
        **kwargs: Any,
    ) -> ToolResult:
        message = kwargs.get(
            "message"
        )

        return ToolResult(
            success=True,
            output=message,
            metadata={
                "tool": self.name,
            },
        )
        