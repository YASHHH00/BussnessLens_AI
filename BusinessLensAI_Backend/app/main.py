"""
BusinessLens AI — Application Entry Point

FastAPI app factory with full lifespan initialization:
1. Logging
2. Database engine
3. Business Field Registry
4. Domain Plugin (populates registry)
5. AI Provider Factory
6. Forecaster Factory
7. Cache Provider
8. Theme Engine
9. Connector Factory
10. Register middleware, exception handlers, routers
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import close_db, init_db
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import get_logger, setup_logging
from app.core.middleware import register_middleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan — startup and shutdown logic.
    All singletons are initialized here and injected into deps.py.
    """
    # ------------------------------------------------------------------ #
    # STARTUP
    # ------------------------------------------------------------------ #
    setup_logging()
    logger.info("Starting %s (env=%s)", settings.APP_NAME, settings.APP_ENV)

    # 1. Database
    init_db()
    logger.info("Database engine initialized: %s", settings.DATABASE_URL.split("@")[-1])

    # 2. Business Field Registry
    from app.registry.field_registry import BusinessFieldRegistry
    registry = BusinessFieldRegistry()

    # 3. Domain Plugin
    from app.plugins.plugin_manager import PluginManager
    plugin_manager = PluginManager(registry)
    plugin = plugin_manager.load_plugin(settings.ACTIVE_DOMAIN_PLUGIN)

    # 4. AI Provider Factory (lazy — no network call at startup)
    from app.ai.provider_factory import ProviderFactory
    ai_provider = ProviderFactory().create()

    # 5. Forecaster Factory (lazy)
    from app.forecasting.forecaster_factory import ForecasterFactory
    forecaster_factory = ForecasterFactory()

    # 6. Cache Provider
    from app.cache.cache_factory import create_cache_provider
    cache = create_cache_provider()

    # 7. Theme Engine
    from app.themes.theme_engine import ThemeEngine
    theme_engine = ThemeEngine()

    # 8. Inject singletons into deps module
    from app.api import deps
    deps.set_singletons(
        registry=registry,
        plugin=plugin,
        cache=cache,
        theme=theme_engine,
        plugin_manager=plugin_manager,
        ai_provider=ai_provider,
    )

    logger.info(
        "Startup complete: plugin=%s, fields=%d, cache=%s",
        plugin.name, len(registry), settings.CACHE_PROVIDER,
    )

    yield

    # ------------------------------------------------------------------ #
    # SHUTDOWN
    # ------------------------------------------------------------------ #
    logger.info("Shutting down %s", settings.APP_NAME)
    await close_db()

    # Close Redis connection if applicable
    if hasattr(cache, "close"):
        await cache.close()

    logger.info("Shutdown complete.")


def create_app() -> FastAPI:
    """Application factory — returns the configured FastAPI instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI-powered self-service Business Intelligence platform. "
            "Connect to any database, map your business fields, and get "
            "instant dashboards, insights, and forecasts."
        ),
        version="1.0.0",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # Middleware (order: CORS → RequestID)
    register_middleware(app)

    # Exception handlers
    register_exception_handlers(app)

    # Routers
    from app.api.v1.router import router as v1_router
    app.include_router(v1_router)

    # Health check (unauthenticated)
    @app.get("/health", tags=["Health"])
    async def health():
        return JSONResponse({"status": "ok", "app": settings.APP_NAME})

    return app


# Module-level app instance (used by uvicorn and tests)
app = create_app()
