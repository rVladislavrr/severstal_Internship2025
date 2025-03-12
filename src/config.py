from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    model_config = SettingsConfigDict(env_file=".env")

    def DATABASE_URL(self):
        return (f"postgresql+asyncpg://"
                f"{self.DB_USER}:{self.DB_PASS}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")

    @property
    def DATABASE_URL_alembic(self):
        return (f"postgresql://"
                f"{self.DB_USER}:{self.DB_PASS}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


settings = Settings()
