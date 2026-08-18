import pytest

from aura.models.providers.mock import MockModelProvider


@pytest.mark.anyio
async def test_mock_provider_generates_response():
    provider = MockModelProvider()

    result = await provider.generate("Hello AURA")

    assert result == "Mock model response to: Hello AURA"


@pytest.mark.anyio
async def test_mock_provider_health_check():
    provider = MockModelProvider()

    healthy = await provider.health_check()

    assert healthy is True


def test_mock_provider_name():
    provider = MockModelProvider()

    assert provider.name == "mock"


def test_mock_provider_model_name():
    provider = MockModelProvider()

    assert provider.model_name == "mock-model"