from aura.core.logger import logger
from aura.models.generation import ModelGenerationResult
from aura.models.providers.base import ModelProvider


class ModelManager:
    def __init__(self):
        self._providers: dict[str, ModelProvider] = {}
        self._default_provider: str | None = None
        self._fallback_provider: str | None = None

    def register_provider(
        self,
        provider: ModelProvider,
        make_default: bool = False,
    ) -> None:
        self._providers[provider.name] = provider

        logger.info(
            "Registered model provider: %s",
            provider.name,
        )

        if make_default or self._default_provider is None:
            self.set_default_provider(provider.name)

    def set_default_provider(self, name: str) -> None:
        if name not in self._providers:
            raise ValueError(
                f"Model provider '{name}' is not registered."
            )

        self._default_provider = name

        logger.info(
            "Default model provider set to: %s",
            name,
        )

    def set_fallback_provider(self, name: str) -> None:
        if name not in self._providers:
            raise ValueError(
                f"Fallback model provider '{name}' is not registered."
            )

        self._fallback_provider = name

        logger.info(
            "Fallback model provider set to: %s",
            name,
        )

    def get_provider(
        self,
        name: str | None = None,
    ) -> ModelProvider:
        provider_name = name or self._default_provider

        if provider_name is None:
            raise RuntimeError(
                "No model provider has been configured."
            )

        provider = self._providers.get(provider_name)

        if provider is None:
            raise ValueError(
                f"Model provider '{provider_name}' is not registered."
            )

        return provider

    async def generate(
        self,
        prompt: str,
        provider_name: str | None = None,
    ) -> ModelGenerationResult:
        provider = self.get_provider(provider_name)

        logger.info(
            "Generating response using provider: %s",
            provider.name,
        )

        try:
            text = await provider.generate(prompt)

            return ModelGenerationResult(
                text=text,
                provider=provider.name,
                model=provider.model_name,
                used_fallback=False,
            )

        except Exception as exc:
            logger.error(
                "Model provider '%s' failed: %s",
                provider.name,
                exc,
            )

            if (
                self._fallback_provider is None
                or provider.name == self._fallback_provider
            ):
                raise

            fallback = self.get_provider(
                self._fallback_provider
            )

            logger.warning(
                "Falling back from '%s' to '%s'",
                provider.name,
                fallback.name,
            )

            text = await fallback.generate(prompt)

            return ModelGenerationResult(
                text=text,
                provider=fallback.name,
                model=fallback.model_name,
                used_fallback=True,
            )

    async def health_check(
        self,
        provider_name: str | None = None,
    ) -> bool:
        provider = self.get_provider(provider_name)

        try:
            return await provider.health_check()

        except Exception as exc:
            logger.error(
                "Health check failed for provider '%s': %s",
                provider.name,
                exc,
            )

            return False

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())

    async def get_provider_statuses(self) -> list[dict]:
        statuses = []

        for name, provider in self._providers.items():
            healthy = await self.health_check(name)

            statuses.append(
                {
                    "name": name,
                    "model": provider.model_name,
                    "healthy": healthy,
                    "default": name == self._default_provider,
                    "fallback": name == self._fallback_provider,
                }
            )

        return statuses

    @property
    def default_provider(self) -> str | None:
        return self._default_provider

    @property
    def fallback_provider(self) -> str | None:
        return self._fallback_provider