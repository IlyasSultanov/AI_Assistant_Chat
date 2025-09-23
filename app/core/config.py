from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class AuthSettings(BaseModel):
    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expires_minutes: int = 3
    refresh_token_expires_minutes: int = 60 * 24 * 14  # 14 дней по умолчанию
    issuer: str = "ai-assistant-chat"
    audience: str = "ai-assistant-clients"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    auth_settings: AuthSettings = AuthSettings()
    db_url: str = Field(
        alias="database_url",
    )


settings = Settings()