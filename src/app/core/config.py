from functools import lru_cache
from typing import Annotated, ClassVar

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    app_name: str = "python-api-template"
    app_version: str = "0.1.0"
    environment: str = Field(default="development")  # development | staging | production
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Interactive docs are exposed everywhere except production. Derived per-instance
    # from `environment` so the value tracks the resolved setting, not a class-body
    # snapshot taken once at import time.
    @property
    def docs_enabled(self) -> bool:
        return self.environment != "production"

    @property
    def docs_url(self) -> str | None:
        return "/docs" if self.docs_enabled else None

    @property
    def redoc_url(self) -> str | None:
        return "/redoc" if self.docs_enabled else None

    @property
    def openapi_url(self) -> str | None:
        return "/openapi.json" if self.docs_enabled else None


@lru_cache
def get_settings() -> Settings:
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
