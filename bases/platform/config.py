from functools import lru_cache
import os


class Settings:
    database_url: str
    swagger_ui_enabled: bool

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
        self.swagger_ui_enabled = os.getenv("SWAGGER_UI_ENABLED", "false").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
