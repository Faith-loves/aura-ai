import pytest

from aura.models.manager import ModelManager
from aura.models.providers.base import ModelProvider
from aura.models.providers.mock import MockModelProvider


class FailingProvider(ModelProvider):
    @property
    def name(self) -> str:
        return "failing"

    @property
    def model_name(self) -> str:
        return "failing-model"

    async def generate(self, prompt: str) -> str:
        raise RuntimeError("Provider unavailable")

    async def health_check(self) -> bool:
        return False


def test_register_provider():
    manager = ModelManager()

    manager.register_provider(
        MockModelProvider()
    )

    assert "mock" in manager.list_providers()


def test_default_provider():
    manager = ModelManager()

    manager.register_provider(
        MockModelProvider(),
        make_default=True,
    )

    assert manager.default_provider == "mock"


def test_get_provider():
    manager = ModelManager()

    manager.register_provider(
        MockModelProvider()
    )

    provider = manager.get_provider("mock")

    assert provider.name == "mock"


@pytest.mark.anyio
async def test_manager_generates_response():
    manager = ModelManager()

    manager.register_provider(
        MockModelProvider(),
        make_default=True,
    )

    result = await manager.generate(
        "Hello AURA"
    )

    assert result.text == (
        "Mock model response to: Hello AURA"
    )

    assert result.provider == "mock"
    assert result.model == "mock-model"
    assert result.used_fallback is False


@pytest.mark.anyio
async def test_manager_health_check():
    manager = ModelManager()

    manager.register_provider(
        MockModelProvider(),
        make_default=True,
    )

    healthy = await manager.health_check()

    assert healthy is True


def test_unknown_provider_raises_error():
    manager = ModelManager()

    manager.register_provider(
        MockModelProvider()
    )

    with pytest.raises(ValueError):
        manager.get_provider("unknown")


def test_set_fallback_provider():
    manager = ModelManager()

    manager.register_provider(
        MockModelProvider()
    )

    manager.set_fallback_provider("mock")

    assert manager.fallback_provider == "mock"


@pytest.mark.anyio
async def test_manager_uses_fallback_when_default_fails():
    manager = ModelManager()

    manager.register_provider(
        FailingProvider()
    )

    manager.register_provider(
        MockModelProvider()
    )

    manager.set_default_provider("failing")
    manager.set_fallback_provider("mock")

    result = await manager.generate(
        "Hello AURA"
    )

    assert result.text == (
        "Mock model response to: Hello AURA"
    )

    assert result.provider == "mock"
    assert result.model == "mock-model"
    assert result.used_fallback is True