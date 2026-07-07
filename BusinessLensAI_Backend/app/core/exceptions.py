"""
BusinessLens AI — Custom Exceptions & FastAPI Exception Handlers

All custom exceptions extend a common base so callers can catch broadly
or specifically. Every unhandled exception returns a consistent JSON envelope:

    {
        "error_code": "NOT_FOUND",
        "message": "The requested resource was not found.",
        "details": { ... }   // optional field-level info
    }
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


# ------------------------------------------------------------------ #
# Base Exception
# ------------------------------------------------------------------ #

class BusinessLensError(Exception):
    """Base class for all application-defined exceptions."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str = "An unexpected error occurred.",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "error_code": self.error_code,
            "message": self.message,
        }
        if self.details:
            payload["details"] = self.details
        return payload


# ------------------------------------------------------------------ #
# 400 — Bad Request / Business Validation
# ------------------------------------------------------------------ #

class ValidationError(BusinessLensError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"

    def __init__(self, message: str = "Validation failed.", details: dict | None = None):
        super().__init__(message, details)


class MappingValidationError(BusinessLensError):
    """Raised when one or more field mapping rules fail."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "MAPPING_VALIDATION_ERROR"

    def __init__(self, errors: list[dict[str, Any]]) -> None:
        super().__init__(
            message="One or more field mappings failed validation.",
            details={"field_errors": errors},
        )


class DataQualityError(BusinessLensError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "DATA_QUALITY_ERROR"


# ------------------------------------------------------------------ #
# 401 / 403 — Auth
# ------------------------------------------------------------------ #

class AuthenticationError(BusinessLensError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_ERROR"

    def __init__(self, message: str = "Authentication required."):
        super().__init__(message)


class AuthorizationError(BusinessLensError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "AUTHORIZATION_ERROR"

    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(message)


class AccountLockedError(BusinessLensError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "ACCOUNT_LOCKED"

    def __init__(self, locked_until: str) -> None:
        super().__init__(
            message=f"Account is temporarily locked due to multiple failed login attempts.",
            details={"locked_until": locked_until},
        )


# ------------------------------------------------------------------ #
# 404 — Not Found
# ------------------------------------------------------------------ #

class NotFoundError(BusinessLensError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"

    def __init__(self, resource: str = "Resource", resource_id: Any = None) -> None:
        msg = f"{resource} not found."
        details = {}
        if resource_id is not None:
            details["id"] = str(resource_id)
        super().__init__(msg, details)


# ------------------------------------------------------------------ #
# 409 — Conflict
# ------------------------------------------------------------------ #

class ConflictError(BusinessLensError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"


# ------------------------------------------------------------------ #
# 422 — Connection / Connector
# ------------------------------------------------------------------ #

class ConnectionTestError(BusinessLensError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "CONNECTION_TEST_FAILED"

    def __init__(self, reason: str) -> None:
        super().__init__(
            message="Database connection test failed.",
            details={"reason": reason},
        )


class ConnectorNotSupportedError(BusinessLensError):
    """Raised when a user requests a DB type whose connector is not yet implemented."""
    status_code = status.HTTP_501_NOT_IMPLEMENTED
    error_code = "CONNECTOR_NOT_SUPPORTED"

    def __init__(self, db_type: str, planned: bool = True) -> None:
        msg = (
            f"The '{db_type}' connector is planned for a future release. "
            "The connector architecture supports adding it without changes to "
            "the Analytics Engine, Semantic Layer, or Dashboard Engine."
            if planned
            else f"The '{db_type}' connector is not supported."
        )
        super().__init__(message=msg, details={"db_type": db_type, "planned": planned})


class SSRFError(BusinessLensError):
    """Raised when a user-supplied connection host is a private/internal IP."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "SSRF_BLOCKED"

    def __init__(self, host: str) -> None:
        super().__init__(
            message="Connection to private/internal IP ranges is not allowed.",
            details={"host": host},
        )


# ------------------------------------------------------------------ #
# 500 — AI / Plugin / Cache
# ------------------------------------------------------------------ #

class AIProviderError(BusinessLensError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "AI_PROVIDER_ERROR"

    def __init__(self, provider: str, reason: str) -> None:
        super().__init__(
            message=f"AI provider '{provider}' failed.",
            details={"provider": provider, "reason": reason},
        )


class PluginError(BusinessLensError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "PLUGIN_ERROR"


class CacheError(BusinessLensError):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "CACHE_ERROR"


class ForecastError(BusinessLensError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "FORECAST_ERROR"

    def __init__(self, reason: str) -> None:
        super().__init__(message="Forecasting failed.", details={"reason": reason})


class SemanticLayerError(BusinessLensError):
    """Raised when the Semantic Layer cannot build or return a SemanticContext."""
    status_code = status.HTTP_409_CONFLICT
    error_code = "SEMANTIC_LAYER_ERROR"

    def __init__(self, reason: str) -> None:
        super().__init__(
            message="Semantic context is unavailable.",
            details={"reason": reason},
        )


class MappingValidationError(BusinessLensError):
    """Raised when a mapping fails one or more business validation rules."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "MAPPING_VALIDATION_ERROR"

    def __init__(self, violations: list[str]) -> None:
        super().__init__(
            message="Mapping validation failed.",
            details={"violations": violations},
        )



# ------------------------------------------------------------------ #
# FastAPI Exception Handlers
# ------------------------------------------------------------------ #

def _json(status_code: int, payload: dict) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all custom exception handlers on the FastAPI application."""

    @app.exception_handler(BusinessLensError)
    async def business_lens_error_handler(
        request: Request, exc: BusinessLensError
    ) -> JSONResponse:
        return _json(exc.status_code, exc.to_dict())

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Convert Pydantic validation errors to a consistent envelope."""
        field_errors = []
        for err in exc.errors():
            field_errors.append(
                {
                    "field": " → ".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                    "type": err["type"],
                }
            )
        return _json(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            {
                "error_code": "REQUEST_VALIDATION_ERROR",
                "message": "Request body or parameters failed validation.",
                "details": {"field_errors": field_errors},
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Catch-all — never expose stack traces to clients."""
        import logging
        logging.getLogger(__name__).exception(
            "Unhandled exception on %s %s", request.method, request.url
        )
        return _json(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            {
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected internal error occurred. Please try again.",
            },
        )
