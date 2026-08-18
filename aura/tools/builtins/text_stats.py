from typing import Any

from aura.tools.base import Tool
from aura.tools.models import (
    ToolParameter,
    ToolParameterType,
    ToolResult,
)


class TextStatsTool(Tool):
    @property
    def name(self) -> str:
        return "text_stats"

    @property
    def description(self) -> str:
        return (
            "Returns basic statistics about "
            "a piece of text."
        )

    @property
    def category(self) -> str:
        return "text"

    @property
    def tags(self) -> list[str]:
        return [
            "text",
            "words",
            "characters",
            "statistics",
        ]

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="text",
                description=(
                    "Text to analyze."
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
        text = kwargs["text"]

        words = text.split()

        lines = text.splitlines()

        non_whitespace_characters = (
            sum(
                1
                for character in text
                if not character.isspace()
            )
        )

        return ToolResult(
            success=True,
            output={
                "characters": len(text),
                "characters_no_whitespace": (
                    non_whitespace_characters
                ),
                "words": len(words),
                "lines": (
                    len(lines)
                    if text
                    else 0
                ),
            },
            metadata={
                "tool": self.name,
            },
        )