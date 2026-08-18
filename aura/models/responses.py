from pydantic import BaseModel


class AuraResponse(BaseModel):
    success: bool
    message: str
    result: str | None = None
    provider: str | None = None
    model: str | None = None
    used_fallback: bool = False