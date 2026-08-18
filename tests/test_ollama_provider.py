import pytest

from aura.models.providers.ollama import OllamaProvider


def test_ollama_provider_name():
    provider = OllamaProvider()

    assert provider.name == "ollama"


def test_ollama_provider_model_name():
    provider = OllamaProvider()

    assert provider.model_name == "llama3.2:3b"


@pytest.mark.anyio
async def test_ollama_health_check():
    provider = OllamaProvider()

    healthy = await provider.health_check()

    assert healthy is True