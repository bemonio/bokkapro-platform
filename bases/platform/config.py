from functools import lru_cache
import os


class Settings:
    database_url: str

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")


@lru_cache
def get_settings() -> Settings:
    return Settings()
