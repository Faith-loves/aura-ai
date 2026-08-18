from aura.core.logger import logger
from aura.tools.base import Tool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(
        self,
        tool: Tool,
        replace: bool = False,
    ) -> None:
        tool_name = tool.name

        if (
            tool_name in self._tools
            and not replace
        ):
            raise ValueError(
                f"Tool '{tool_name}' "
                "is already registered."
            )

        self._tools[tool_name] = tool

        logger.info(
            "Registered tool | name=%s",
            tool_name,
        )

    def unregister(
        self,
        name: str,
    ) -> bool:
        if name not in self._tools:
            return False

        del self._tools[name]

        logger.info(
            "Unregistered tool | name=%s",
            name,
        )

        return True

    def get(
        self,
        name: str,
    ) -> Tool:
        tool = self._tools.get(
            name
        )

        if tool is None:
            raise ValueError(
                f"Tool '{name}' "
                "is not registered."
            )

        return tool

    def find(
        self,
        name: str,
    ) -> Tool | None:
        return self._tools.get(
            name
        )

    def exists(
        self,
        name: str,
    ) -> bool:
        return (
            name in self._tools
        )

    def list_tools(
        self,
    ) -> list[Tool]:
        return list(
            self._tools.values()
        )

    def list_names(
        self,
    ) -> list[str]:
        return list(
            self._tools.keys()
        )

    def get_schemas(
        self,
    ) -> list[dict]:
        return [
            tool.get_schema()
            for tool
            in self._tools.values()
        ]

    def count(
        self,
    ) -> int:
        return len(
            self._tools
        )

    def clear(
        self,
    ) -> int:
        count = len(
            self._tools
        )

        self._tools.clear()

        logger.info(
            "Cleared tool registry | "
            "removed=%s",
            count,
        )

        return count