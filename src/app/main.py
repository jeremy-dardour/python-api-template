from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.core.router import api_router
from app.health.router import router as health_router

settings = get_settings()
setup_logging(
    json_output=settings.environment == "production",
    log_level=settings.log_level,
    # environment is intentionally omitted: it is a deployment fact the log shipper/collector
    # should tag, kept consistent across services rather than self-reported by the app.
    static_fields={
        "service": settings.app_name,
        "version": settings.app_version,
    },
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)

app.add_middleware(SecurityHeadersMiddleware, environment=settings.environment)

# Default-closed: no origins allowed until CORS_ORIGINS is set.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Added last so it is the outermost middleware: request_id is bound before any other layer runs,
# and duration_ms measures the full request rather than only the inner application slice.
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)
app.include_router(health_router)
app.include_router(api_router, prefix=settings.api_prefix)
