from pathlib import Path
from pydantic import BaseModel
from pydantic.v1 import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class AuthSettings(BaseModel):
    private_key: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expires_minutes: int = 3
    refresh_token_expires_minutes: int = 60 * 24 * 14  # 14 дней по умолчанию
    issuer: str = "ai-assistant-chat"
    audience: str = "ai-assistant-clients"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    db_url: str = Field(alias="DB_URL", env_file=BASE_DIR / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")
    auth_settings: AuthSettings = AuthSettings()
    database: DatabaseSettings = DatabaseSettings()


settings = Settings()
