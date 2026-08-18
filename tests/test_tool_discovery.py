from aura.tools.base import Tool
from aura.tools.discovery import ToolDiscovery
from aura.tools.models import ToolResult
from aura.tools.registry import ToolRegistry


class SearchTool(Tool):
    @property
    def name(self) -> str:
        return "search"

    @property
    def description(self) -> str:
        return (
            "Search for information."
        )

    @property
    def category(self) -> str:
        return "information"

    @property
    def tags(self) -> list[str]:
        return [
            "web",
            "search",
            "research",
        ]

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True
        )


class CalculatorTool(Tool):
    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return (
            "Perform mathematical calculations."
        )

    @property
    def category(self) -> str:
        return "utility"

    @property
    def tags(self) -> list[str]:
        return [
            "math",
            "calculate",
        ]

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True
        )


class DeleteTool(Tool):
    @property
    def name(self) -> str:
        return "delete_file"

    @property
    def description(self) -> str:
        return (
            "Delete a file from disk."
        )

    @property
    def category(self) -> str:
        return "filesystem"

    @property
    def dangerous(self) -> bool:
        return True

    @property
    def requires_confirmation(
        self,
    ) -> bool:
        return True

    @property
    def tags(self) -> list[str]:
        return [
            "file",
            "delete",
        ]

    async def execute(
        self,
        **kwargs,
    ) -> ToolResult:
        return ToolResult(
            success=True
        )


def create_discovery():
    registry = ToolRegistry()

    registry.register(
        SearchTool()
    )

    registry.register(
        CalculatorTool()
    )

    registry.register(
        DeleteTool()
    )

    return ToolDiscovery(
        registry=registry
    )


def test_search_by_name():
    discovery = create_discovery()

    tools = discovery.search(
        "calculator"
    )

    assert len(tools) == 1

    assert (
        tools[0].name
        == "calculator"
    )


def test_search_by_description():
    discovery = create_discovery()

    tools = discovery.search(
        "mathematical"
    )

    assert len(tools) == 1

    assert (
        tools[0].name
        == "calculator"
    )


def test_search_by_category():
    discovery = create_discovery()

    tools = discovery.search(
        "information"
    )

    assert len(tools) == 1

    assert (
        tools[0].name
        == "search"
    )


def test_search_by_tag():
    discovery = create_discovery()

    tools = discovery.search(
        "research"
    )

    assert len(tools) == 1

    assert (
        tools[0].name
        == "search"
    )


def test_search_is_case_insensitive():
    discovery = create_discovery()

    tools = discovery.search(
        "CALCULATOR"
    )

    assert len(tools) == 1

    assert (
        tools[0].name
        == "calculator"
    )


def test_empty_search_returns_empty_list():
    discovery = create_discovery()

    assert (
        discovery.search("   ")
        == []
    )


def test_find_by_category():
    discovery = create_discovery()

    tools = discovery.find_by_category(
        "utility"
    )

    assert len(tools) == 1

    assert (
        tools[0].name
        == "calculator"
    )


def test_find_by_tag():
    discovery = create_discovery()

    tools = discovery.find_by_tag(
        "web"
    )

    assert len(tools) == 1

    assert (
        tools[0].name
        == "search"
    )


def test_find_safe_tools():
    discovery = create_discovery()

    tools = discovery.find_safe_tools()

    names = {
        tool.name
        for tool in tools
    }

    assert names == {
        "search",
        "calculator",
    }


def test_find_confirmation_tools():
    discovery = create_discovery()

    tools = (
        discovery.find_confirmation_tools()
    )

    assert len(tools) == 1

    assert (
        tools[0].name
        == "delete_file"
    )