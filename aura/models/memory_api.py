from pydantic import BaseModel, Field

from aura.memory.models import MemoryType


class CreateMemoryRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
    )

    memory_type: MemoryType

    importance: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
    )

    metadata: dict = Field(
        default_factory=dict
    )


class SearchMemoryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
    )

    limit: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    memory_type: MemoryType | None = None


class MemoryResponse(BaseModel):
    id: str
    memory_type: MemoryType
    content: str
    importance: float
    access_count: int
    metadata: dict


class MemorySearchResult(BaseModel):
    memory: MemoryResponse
    score: float


class ImportMemoryRequest(BaseModel):
    version: int = 1
    memories: list[dict]


class RestoreMemoryRequest(BaseModel):
    file_path: str = Field(
        ...,
        min_length=1,
    )

    clear_existing: bool = True