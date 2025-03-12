from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    DB_HOST_TEST: str
    DB_PORT_TEST: str
    DB_NAME_TEST: str
    DB_USER_TEST: str
    DB_PASS_TEST: str


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

    def DATABASE_URL_TEST(self):
        return (f"postgresql+asyncpg://"
                f"{self.DB_USER_TEST}:{self.DB_PASS_TEST}"
                f"@{self.DB_HOST_TEST}:{self.DB_PORT_TEST}/{self.DB_NAME_TEST}")


settings = Settings()
