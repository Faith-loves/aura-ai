from aura.core.container import Container
from aura.execution.binding import (
    ToolBindingManager,
)
from aura.execution.manager import (
    ExecutionManager,
)
from aura.execution.runner import (
    ExecutionRunner,
)
from aura.execution.store import (
    ExecutionStore,
)
from aura.planning.planner import Planner
from aura.tools.discovery import (
    ToolDiscovery,
)
from aura.tools.executor import (
    ToolExecutor,
)
from aura.tools.registry import (
    ToolRegistry,
)
from aura.tools.validator import (
    ToolArgumentValidator,
)


def test_container_initializes():
    container = Container()

    assert container.model_manager is not None

    assert container.memory_manager is not None

    assert isinstance(
        container.planner,
        Planner,
    )

    assert container.plan_store is not None

    assert isinstance(
        container.execution_store,
        ExecutionStore,
    )

    assert isinstance(
        container.execution_manager,
        ExecutionManager,
    )

    assert isinstance(
        container.tool_registry,
        ToolRegistry,
    )

    assert isinstance(
        container.tool_discovery,
        ToolDiscovery,
    )

    assert isinstance(
        container.tool_validator,
        ToolArgumentValidator,
    )

    assert isinstance(
        container.tool_executor,
        ToolExecutor,
    )

    assert isinstance(
        container.tool_binding_manager,
        ToolBindingManager,
    )

    assert isinstance(
        container.execution_runner,
        ExecutionRunner,
    )

    assert container.kernel is not None


def test_execution_manager_uses_container_store():
    container = Container()

    assert (
        container.execution_manager.store
        is container.execution_store
    )


def test_execution_manager_uses_container_planner():
    container = Container()

    assert (
        container.execution_manager.planner
        is container.planner
    )


def test_tool_binding_uses_container_registry():
    container = Container()

    assert (
        container.tool_binding_manager.registry
        is container.tool_registry
    )


def test_tool_binding_uses_container_discovery():
    container = Container()

    assert (
        container.tool_binding_manager.discovery
        is container.tool_discovery
    )


def test_execution_runner_uses_manager():
    container = Container()

    assert (
        container.execution_runner
        .execution_manager
        is container.execution_manager
    )


def test_execution_runner_uses_tool_executor():
    container = Container()

    assert (
        container.execution_runner
        .tool_executor
        is container.tool_executor
    )


def test_execution_runner_uses_binding_manager():
    container = Container()

    assert (
        container.execution_runner
        .tool_binding_manager
        is container.tool_binding_manager
    )


def test_container_execution_store_starts_empty():
    container = Container()

    assert (
        container.execution_store.count()
        == 0
    )


def test_container_registers_builtin_tools():
    container = Container()

    expected_tools = {
        "echo",
        "system_info",
        "calculator",
        "current_time",
        "text_stats",
    }

    assert set(
        container.tool_registry.list_names()
    ) == expected_tools

    assert (
        container.tool_registry.count()
        == 5
    )


def test_kernel_uses_container_tools():
    container = Container()

    assert (
        container.kernel.tool_discovery
        is container.tool_discovery
    )

    assert (
        container.kernel.tool_executor
        is container.tool_executor
    )


def test_tool_executor_uses_container_registry():
    container = Container()

    assert (
        container.tool_executor.registry
        is container.tool_registry
    )


def test_container_starts_not_ready():
    container = Container()

    assert (
        container.is_ready()
        is False
    )


def test_container_initialize():
    container = Container()

    container.initialize()

    assert (
        container.is_ready()
        is True
    )

    assert (
        container.kernel.is_ready()
        is True
    )

    container.shutdown()


def test_container_shutdown():
    container = Container()

    container.initialize()

    container.shutdown()

    assert (
        container.is_ready()
        is False
    )

    assert (
        container.kernel.is_ready()
        is False
    )


def test_kernel_uses_container_planner():
    container = Container()

    assert (
        container.kernel.planner
        is container.planner
    )