from pydantic import BaseModel


class AuraSettings(BaseModel):
    app_name: str = "AURA"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    model_provider: str = "ollama"
    model_name: str = "llama3.2:3b"
    ollama_base_url: str = "http://localhost:11434"


settings = AuraSettings()