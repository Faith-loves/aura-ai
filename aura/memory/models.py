from datetime import UTC, datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    CONVERSATION = "conversation"
    FACT = "fact"
    PREFERENCE = "preference"
    PROJECT = "project"
    TASK = "task"
    SYSTEM = "system"


class MemoryRecord(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4())
    )

    memory_type: MemoryType

    content: str = Field(
        ...,
        min_length=1,
    )

    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )

    access_count: int = Field(
        default=0,
        ge=0,
    )

    last_accessed_at: datetime | None = None

    metadata: dict = Field(
        default_factory=dict
    )