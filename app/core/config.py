from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class AuthSettings(BaseModel):
    private_key: Path = BASE_DIR / "keys" / "jwt-private_key.pem"
    public_key: Path = BASE_DIR / "keys" / "jwt-public_key.pem"
    algorithm: str = "RS256"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    auth_settings: AuthSettings = AuthSettings()


settings = Settings()