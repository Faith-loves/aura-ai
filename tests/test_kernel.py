import pytest

from aura.core.kernel import AuraKernel
from aura.memory.formatter import MemoryFormatter
from aura.memory.manager import MemoryManager
from aura.memory.models import MemoryType
from aura.memory.repository import MemoryRepository
from aura.memory.scorer import MemoryScorer
from aura.models.manager import ModelManager
from aura.models.providers.mock import MockModelProvider
from aura.models.requests import AuraRequest
from aura.planning.models import (
    PlanStatus,
    PlanStepStatus,
)
from aura.planning.planner import Planner
from aura.tools.discovery import ToolDiscovery
from aura.tools.executor import ToolExecutor
from aura.tools.loader import ToolLoader
from aura.tools.registry import ToolRegistry
from aura.tools.validator import ToolArgumentValidator


def create_test_kernel(
    tmp_path,
):
    model_manager = ModelManager()

    model_manager.register_provider(
        MockModelProvider(),
        make_default=True,
    )

    repository = MemoryRepository(
        database_path=str(
            tmp_path
            / "kernel_memory.db"
        )
    )

    memory_manager = MemoryManager(
        repository=repository,
        scorer=MemoryScorer(),
        formatter=MemoryFormatter(),
    )

    planner = Planner()

    tool_registry = ToolRegistry()

    tool_loader = ToolLoader(
        registry=tool_registry
    )

    tool_loader.load_builtin_tools()

    tool_discovery = ToolDiscovery(
        registry=tool_registry
    )

    tool_executor = ToolExecutor(
        registry=tool_registry,
        validator=(
            ToolArgumentValidator()
        ),
    )

    return AuraKernel(
        model_manager=model_manager,
        memory_manager=memory_manager,
        planner=planner,
        tool_discovery=tool_discovery,
        tool_executor=tool_executor,
    )


def test_kernel_initializes(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    assert (
        kernel.is_ready()
        is False
    )

    kernel.initialize()

    assert (
        kernel.is_ready()
        is True
    )

    kernel.shutdown()

    assert (
        kernel.is_ready()
        is False
    )


@pytest.mark.anyio
async def test_kernel_processes_request(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    kernel.initialize()

    request = AuraRequest(
        message="Explain what AURA is."
    )

    response = await kernel.process(
        request
    )

    assert response.success is True

    assert response.message == (
        "Task completed successfully."
    )

    assert response.result.startswith(
        "Mock model response to:"
    )

    assert response.provider == "mock"
    assert response.model == "mock-model"

    assert (
        response.used_fallback
        is False
    )

    kernel.shutdown()


@pytest.mark.anyio
async def test_kernel_status_reports_tools(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    kernel.initialize()

    status = await kernel.get_status()

    assert (
        status["tool_count"]
        == 5
    )

    assert (
        status["tool_executor_available"]
        is True
    )

    kernel.shutdown()


def test_kernel_can_create_plan(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    kernel.initialize()

    plan = kernel.create_plan(
        "Build a REST API."
    )

    assert plan.goal == (
        "Build a REST API."
    )

    assert (
        plan.status
        == PlanStatus.PENDING
    )

    assert len(plan.steps) == 6

    kernel.shutdown()


def test_kernel_can_start_plan(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    kernel.initialize()

    plan = kernel.create_plan(
        "Build a REST API."
    )

    kernel.start_plan(
        plan
    )

    assert (
        plan.status
        == PlanStatus.IN_PROGRESS
    )

    assert (
        plan.steps[0].status
        == PlanStepStatus.READY
    )

    kernel.shutdown()


def test_kernel_can_list_tools(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    kernel.initialize()

    tools = kernel.list_tools()

    names = {
        tool["name"]
        for tool in tools
    }

    assert names == {
        "echo",
        "system_info",
        "calculator",
        "current_time",
        "text_stats",
    }

    kernel.shutdown()


def test_kernel_can_discover_tool(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    kernel.initialize()

    tools = kernel.discover_tools(
        "math"
    )

    names = {
        tool["name"]
        for tool in tools
    }

    assert (
        "calculator"
        in names
    )

    kernel.shutdown()


@pytest.mark.anyio
async def test_kernel_can_execute_echo_tool(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    kernel.initialize()

    result = await kernel.execute_tool(
        tool_name="echo",
        arguments={
            "message": "Hello AURA",
        },
    )

    assert result.success is True

    assert (
        result.output
        == "Hello AURA"
    )

    assert (
        result.tool_name
        == "echo"
    )

    kernel.shutdown()


@pytest.mark.anyio
async def test_kernel_can_execute_calculator(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    kernel.initialize()

    result = await kernel.execute_tool(
        tool_name="calculator",
        arguments={
            "operation": "add",
            "a": 10.0,
            "b": 5.0,
        },
    )

    assert result.success is True
    assert result.output == 15.0

    kernel.shutdown()


@pytest.mark.anyio
async def test_kernel_tool_failure_is_structured(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    kernel.initialize()

    result = await kernel.execute_tool(
        tool_name="missing_tool"
    )

    assert result.success is False

    assert (
        result.error_code
        == "tool_not_found"
    )

    kernel.shutdown()


def test_kernel_tools_require_ready_kernel(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    with pytest.raises(
        RuntimeError,
        match="Kernel is not ready",
    ):
        kernel.list_tools()


def test_should_not_store_short_message(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    assert (
        kernel._should_store_memory(
            "Hi"
        )
        is False
    )


def test_should_store_useful_message(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    assert (
        kernel._should_store_memory(
            "My project uses FastAPI "
            "and SQLite."
        )
        is True
    )


def test_classify_project_memory(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    memory_type = (
        kernel._classify_memory_type(
            "My project uses "
            "FastAPI and SQLite."
        )
    )

    assert (
        memory_type
        == MemoryType.PROJECT
    )


def test_detects_contaminated_memory(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    contaminated = (
        "Relevant memory context:\n\n"
        "Memory 1\n"
        "Content: AURA uses FastAPI.\n\n"
        "Current user request:\n"
        "Hello AURA"
    )

    assert (
        kernel._is_contaminated_memory(
            contaminated
        )
        is True
    )


def test_clean_memory_is_not_contaminated(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    assert (
        kernel._is_contaminated_memory(
            "FastAPI is a Python "
            "web framework."
        )
        is False
    )


def test_mock_response_removes_memory_context(
    tmp_path,
):
    kernel = create_test_kernel(
        tmp_path
    )

    memory_context = (
        "Relevant memory context:\n\n"
        "Memory 1\n"
        "Type: project\n"
        "Content: AURA uses FastAPI."
    )

    raw_response = (
        "Mock model response to: "
        f"{memory_context}\n\n"
        "Current user request:\n"
        "Hello AURA\n\n"
        "Use the relevant memory context "
        "only when it helps answer "
        "the current request."
    )

    cleaned = (
        kernel._clean_assistant_response(
            raw_response=raw_response,
            user_message="Hello AURA",
            memory_context=memory_context,
            provider="mock",
        )
    )

    assert cleaned == (
        "Mock model response to: "
        "Hello AURA"
    )