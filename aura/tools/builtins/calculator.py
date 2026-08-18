from typing import Any

from aura.tools.base import Tool
from aura.tools.models import (
    ToolParameter,
    ToolParameterType,
    ToolResult,
)


class CalculatorTool(Tool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Performs basic arithmetic operations "
            "on two numbers."
        )

    @property
    def category(self) -> str:
        return "utility"

    @property
    def tags(self) -> list[str]:
        return [
            "math",
            "calculator",
            "arithmetic",
        ]

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                description=(
                    "Arithmetic operation to perform."
                ),
                parameter_type=(
                    ToolParameterType.STRING
                ),
                required=True,
                choices=[
                    "add",
                    "subtract",
                    "multiply",
                    "divide",
                ],
            ),
            ToolParameter(
                name="a",
                description="First number.",
                parameter_type=(
                    ToolParameterType.FLOAT
                ),
                required=True,
            ),
            ToolParameter(
                name="b",
                description="Second number.",
                parameter_type=(
                    ToolParameterType.FLOAT
                ),
                required=True,
            ),
        ]

    async def execute(
        self,
        **kwargs: Any,
    ) -> ToolResult:
        operation = kwargs["operation"]
        a = kwargs["a"]
        b = kwargs["b"]

        if operation == "add":
            result = a + b

        elif operation == "subtract":
            result = a - b

        elif operation == "multiply":
            result = a * b

        elif operation == "divide":
            if b == 0:
                return ToolResult(
                    success=False,
                    error=(
                        "Division by zero is not allowed."
                    ),
                    metadata={
                        "tool": self.name,
                    },
                )

            result = a / b

        else:
            return ToolResult(
                success=False,
                error=(
                    f"Unsupported operation: "
                    f"{operation}"
                ),
                metadata={
                    "tool": self.name,
                },
            )

        return ToolResult(
            success=True,
            output=result,
            metadata={
                "tool": self.name,
                "operation": operation,
            },
        )