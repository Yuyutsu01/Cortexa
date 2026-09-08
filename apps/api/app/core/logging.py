"""Structured Logging Configuration.

Configures Python's standard logging module with consistent formats and correlation support.
"""

import logging
import sys


class CortexaFormatter(logging.Formatter):
    """Custom formatter that includes request correlation context if available."""

    def format(self, record: logging.LogRecord) -> str:
        # Default request_id to '-' if not attached to record
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return super().format(record)


def setup_logging(log_level: str | None = None) -> logging.Logger:
    """Initialize root logger format and handlers."""
    level = log_level or "INFO"
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    log_format = (
        "[%(asctime)s] [%(levelname)s] [req_id:%(request_id)s] "
        "[%(name)s:%(funcName)s:%(lineno)d] - %(message)s"
    )

    formatter = CortexaFormatter(fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    # Clear existing handlers from root logger to prevent duplicate logs
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers = []

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set third-party loggers to a reasonable default
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").addHandler(console_handler)

    logger = logging.getLogger("cortexa")
    logger.info("Logging system initialized at level %s", level.upper())
    return logger
