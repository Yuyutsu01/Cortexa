"""Application Middleware Module.

Provides request ID correlation, processing time headers, and request logging.
"""

import logging
import time
import uuid

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware that attaches a unique X-Request-ID header to every request/response cycle."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Extract or generate correlation ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()

        # Process the request downstream
        response = await call_next(request)

        process_time = (time.perf_counter() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"

        # Log request completion with timing
        logger.info(
            "%s %s - Status: %d - %.2fms",
            request.method,
            request.url.path,
            response.status_code,
            process_time,
            extra={"request_id": request_id},
        )

        return response


def register_middlewares(app: FastAPI) -> None:
    """Register custom middlewares on the FastAPI application."""
    app.add_middleware(RequestCorrelationMiddleware)
