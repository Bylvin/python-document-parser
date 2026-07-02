from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Document Parser API"
    VERSION:str = "0.0.1"
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 104857600

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

Path(settings.UPLOAD_DIR).mkdir(
    parents=True,
    exist_ok=True
)
