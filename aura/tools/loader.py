from aura.core.logger import logger
from aura.tools.builtins import (
    CalculatorTool,
    CurrentTimeTool,
    EchoTool,
    SystemInfoTool,
    TextStatsTool,
)
from aura.tools.registry import ToolRegistry


class ToolLoader:
    def __init__(
        self,
        registry: ToolRegistry,
    ):
        self.registry = registry

    def load_builtin_tools(
        self,
    ) -> int:
        tools = [
            EchoTool(),
            SystemInfoTool(),
            CalculatorTool(),
            CurrentTimeTool(),
            TextStatsTool(),
        ]

        registered = 0

        for tool in tools:
            if self.registry.exists(
                tool.name
            ):
                logger.info(
                    "Built-in tool already "
                    "registered | name=%s",
                    tool.name,
                )

                continue

            self.registry.register(
                tool
            )

            registered += 1

        logger.info(
            "Built-in tool loading "
            "completed | registered=%s",
            registered,
        )

        return registered