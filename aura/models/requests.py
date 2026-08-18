from pydantic import BaseModel, Field


class AuraRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="The task or message submitted to AURA",
    )