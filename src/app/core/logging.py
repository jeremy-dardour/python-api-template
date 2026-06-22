import logging
import sys
from collections.abc import Callable

import structlog

StaticFieldsProcessor = Callable[
    [structlog.types.WrappedLogger, str, structlog.types.EventDict],
    structlog.types.EventDict,
]


def _add_static_fields(fields: dict[str, str]) -> StaticFieldsProcessor:
    """Inject fixed service metadata (service, version) into every event."""

    def processor(
        _logger: object,
        _method_name: str,
        event_dict: structlog.types.EventDict,
    ) -> structlog.types.EventDict:
        for key, value in fields.items():
            event_dict.setdefault(key, value)
        return event_dict

    return processor


def _silence_duplicate_uvicorn_access_log() -> None:
    """Drop uvicorn's own access log; RequestLoggingMiddleware already emits a structured one."""
    access_logger = logging.getLogger("uvicorn.access")
    access_logger.handlers.clear()
    access_logger.propagate = False


def _route_uvicorn_through_root() -> None:
    """Make uvicorn's loggers propagate to the root handler so they share our renderer."""
    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True


def setup_logging(
    *,
    json_output: bool,
    log_level: str = "INFO",
    static_fields: dict[str, str] | None = None,
) -> None:
    """Configure structlog and stdlib logging with shared rendering and service metadata."""
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        _add_static_fields(static_fields or {}),
    ]

    if json_output:
        # default=str renders UUID/datetime as clean values instead of repr() noise.
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer(default=str)
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # foreign_pre_chain applies the same processors to stdlib/third-party records (uvicorn),
        # so their output carries the same timestamp, level, and service metadata.
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level.upper())

    _route_uvicorn_through_root()
    _silence_duplicate_uvicorn_access_log()
