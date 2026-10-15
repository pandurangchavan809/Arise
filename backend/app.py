"""
Main FastAPI Application for Adaptive Memory Runtime.
Configures structured logging, CORS, request tracing, lifecycle management, and route registration.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from backend.dependencies import cleanup_dependencies, get_storage
from backend.routes import (
    assistant_router,
    memories_router,
    memory_ops_router,
    system_router,
)

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Initializes storage backend on startup and releases connections on shutdown.
    """
    logger.info("Initializing Adaptive Memory Runtime backend...")
    storage = await get_storage()
    await storage.initialize()
    logger.info("Adaptive Memory Runtime backend initialized successfully.")
    yield
    logger.info("Shutting down Adaptive Memory Runtime backend...")
    await cleanup_dependencies()
    logger.info("Adaptive Memory Runtime backend shutdown complete.")


def create_app() -> FastAPI:
    """FastAPI application factory."""
    app = FastAPI(
        title="Adaptive Memory Runtime API",
        description="Production-grade deterministic memory middleware for AI agents.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request ID and latency tracing middleware
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.perf_counter()

        # Bind context to structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path)

        try:
            response: Response = await call_next(request)
        except Exception as exc:
            logger.error("Unhandled request exception", error=str(exc))
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "request_id": request_id},
            )

        process_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = str(process_time_ms)
        return response

    # Exception Handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning("Request validation failed", errors=exc.errors())
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors()},
        )

    # Include Routers
    app.include_router(memories_router)
    app.include_router(memory_ops_router)
    app.include_router(assistant_router)
    app.include_router(system_router)

    @app.get("/")
    async def root():
        """Root endpoint confirming service running."""
        return {
            "name": "Adaptive Memory Runtime",
            "version": "0.1.0",
            "status": "operational",
            "docs": "/docs",
        }

    @app.get("/health")
    async def health_alias():
        """Top-level health check endpoint for container probes."""
        return {"status": "healthy", "service": "adaptive-memory-runtime"}

    return app


app = create_app()
