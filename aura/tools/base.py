from abc import ABC, abstractmethod
from typing import Any

from aura.tools.models import (
    ToolMetadata,
    ToolParameter,
    ToolResult,
)


class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError

    @property
    def category(self) -> str:
        return "general"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def dangerous(self) -> bool:
        return False

    @property
    def requires_confirmation(
        self,
    ) -> bool:
        return False

    @property
    def tags(self) -> list[str]:
        return []

    @property
    def parameters(
        self,
    ) -> list[ToolParameter]:
        return []

    @abstractmethod
    async def execute(
        self,
        **kwargs: Any,
    ) -> ToolResult:
        raise NotImplementedError

    def get_metadata(
        self,
    ) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
            category=self.category,
            version=self.version,
            dangerous=self.dangerous,
            requires_confirmation=(
                self.requires_confirmation
            ),
            tags=self.tags,
            parameters=self.parameters,
        )

    def get_schema(
        self,
    ) -> dict:
        return (
            self.get_metadata()
            .model_dump(
                mode="json"
            )
        )

    def required_parameters(
        self,
    ) -> list[str]:
        return [
            parameter.name
            for parameter in self.parameters
            if parameter.required
        ]