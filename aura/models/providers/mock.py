from aura.models.providers.base import ModelProvider


class MockModelProvider(ModelProvider):
    @property
    def name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock-model"

    async def generate(self, prompt: str) -> str:
        return f"Mock model response to: {prompt}"

    async def health_check(self) -> bool:
        return True