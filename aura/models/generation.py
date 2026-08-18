from pydantic import BaseModel


class ModelGenerationResult(BaseModel):
    text: str
    provider: str
    model: str
    used_fallback: bool = False