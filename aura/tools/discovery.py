from aura.tools.base import Tool
from aura.tools.registry import ToolRegistry


class ToolDiscovery:
    def __init__(
        self,
        registry: ToolRegistry,
    ):
        self.registry = registry

    def search(
        self,
        query: str,
    ) -> list[Tool]:
        cleaned_query = (
            query.strip().lower()
        )

        if not cleaned_query:
            return []

        matches = []

        for tool in self.registry.list_tools():
            if self._matches_query(
                tool,
                cleaned_query,
            ):
                matches.append(
                    tool
                )

        return sorted(
            matches,
            key=lambda tool: tool.name,
        )

    def find_by_category(
        self,
        category: str,
    ) -> list[Tool]:
        cleaned_category = (
            category.strip().lower()
        )

        return sorted(
            [
                tool
                for tool
                in self.registry.list_tools()
                if (
                    tool.category.lower()
                    == cleaned_category
                )
            ],
            key=lambda tool: tool.name,
        )

    def find_by_tag(
        self,
        tag: str,
    ) -> list[Tool]:
        cleaned_tag = (
            tag.strip().lower()
        )

        matches = []

        for tool in self.registry.list_tools():
            normalized_tags = {
                existing_tag.lower()
                for existing_tag
                in tool.tags
            }

            if cleaned_tag in normalized_tags:
                matches.append(
                    tool
                )

        return sorted(
            matches,
            key=lambda tool: tool.name,
        )

    def find_safe_tools(
        self,
    ) -> list[Tool]:
        return sorted(
            [
                tool
                for tool
                in self.registry.list_tools()
                if not tool.dangerous
            ],
            key=lambda tool: tool.name,
        )

    def find_confirmation_tools(
        self,
    ) -> list[Tool]:
        return sorted(
            [
                tool
                for tool
                in self.registry.list_tools()
                if tool.requires_confirmation
            ],
            key=lambda tool: tool.name,
        )

    def _matches_query(
        self,
        tool: Tool,
        query: str,
    ) -> bool:
        searchable_values = [
            tool.name.lower(),
            tool.description.lower(),
            tool.category.lower(),
        ]

        searchable_values.extend(
            tag.lower()
            for tag in tool.tags
        )

        return any(
            query in value
            for value in searchable_values
        )