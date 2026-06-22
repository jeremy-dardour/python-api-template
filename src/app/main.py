from fastapi import FastAPI

from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.router import api_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_prefix)
