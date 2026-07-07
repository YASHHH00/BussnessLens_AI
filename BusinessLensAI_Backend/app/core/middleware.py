"""
BusinessLens AI — Middleware: CORS, Request ID, Rate Limiting
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------ #
# Rate Limiter (module-level — shared across all routers)
# ------------------------------------------------------------------ #

limiter = Limiter(key_func=get_remote_address, enabled=settings.RATE_LIMIT_ENABLED)


# ------------------------------------------------------------------ #
# Request-ID Middleware
# ------------------------------------------------------------------ #

class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Injects a unique X-Request-ID header into every request and response.
    If the client sends X-Request-ID, we use it; otherwise we generate one.
    Useful for log correlation across distributed services.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


# ------------------------------------------------------------------ #
# Registration function
# ------------------------------------------------------------------ #

def register_middleware(app: FastAPI) -> None:
    """
    Register all middleware on the FastAPI application.
    Order matters — middleware is applied last-registered-first-executed (LIFO).
    """
    # 1. Rate limiting state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # 2. CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. Request ID (runs innermost — applied after CORS)
    app.add_middleware(RequestIDMiddleware)

    logger.info(
        "Middleware registered: CORS origins=%s, rate_limit_enabled=%s",
        settings.allowed_origins_list,
        settings.RATE_LIMIT_ENABLED,
    )
