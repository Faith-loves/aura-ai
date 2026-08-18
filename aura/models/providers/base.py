from abc import ABC, abstractmethod


class ModelProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the active model name."""
        pass

    @abstractmethod
    async def generate(self, prompt: str) -> str:
        """Generate a response from the model."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check whether the provider is available."""
        pass