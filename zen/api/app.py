"""FastAPI application factory for the zenOS REST API."""

from __future__ import annotations

import os
from typing import List, Optional, Sequence

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from zen import __version__
from zen.api.envelope import make_error
from zen.api.errors import PacketError
from zen.api.routers.health import health_router, meta_router
from zen.api.routers.session import router as session_router
from zen.api.state import ApiState
from zen.services.errors import ServiceError

_UNSET = object()

DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
)


def _cors_origins(explicit: Optional[Sequence[str]] = None) -> List[str]:
    if explicit is not None:
        return [origin.strip() for origin in explicit if origin.strip()]
    raw = os.getenv("ZEN_API_CORS", "")
    if raw.strip():
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return list(DEFAULT_CORS_ORIGINS)


def _resolve_token(api_token: object) -> Optional[str]:
    if api_token is _UNSET:
        return os.getenv("ZEN_API_TOKEN") or None
    return api_token or None  # type: ignore[return-value]


def create_app(
    *,
    api_token: Optional[str] = _UNSET,  # type: ignore[assignment]
    cors_origins: Optional[Sequence[str]] = None,
    state: Optional[ApiState] = None,
) -> FastAPI:
    """Build the zenOS HTTP app. Pass api_token=None to disable auth explicitly."""
    app = FastAPI(
        title="zenOS API",
        description="Machine interface for zenOS agents, Dex, plugins, and inbox.",
        version=__version__,
    )
    resolved_token = _resolve_token(api_token)
    if state is None:
        app.state.zen = ApiState(api_token=resolved_token)
    else:
        app.state.zen = state
        if api_token is not _UNSET:
            app.state.zen.api_token = resolved_token

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Zen-Session"],
    )

    @app.exception_handler(PacketError)
    async def packet_error_handler(request: Request, exc: PacketError) -> JSONResponse:
        sid = request.headers.get("x-zen-session")
        seq = request.app.state.zen.sessions.next_seq(sid)
        packet = make_error(exc.code, exc.message, details=exc.details, sid=sid, seq=seq)
        return JSONResponse(status_code=exc.status_code, content=packet.to_wire())

    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
        sid = request.headers.get("x-zen-session")
        seq = request.app.state.zen.sessions.next_seq(sid)
        packet = make_error(exc.code, exc.message, details=exc.details, sid=sid, seq=seq)
        return JSONResponse(status_code=exc.status_code, content=packet.to_wire())

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        sid = request.headers.get("x-zen-session")
        seq = request.app.state.zen.sessions.next_seq(sid)
        packet = make_error(
            "validation_error",
            "Request validation failed",
            details={"errors": exc.errors()},
            sid=sid,
            seq=seq,
        )
        return JSONResponse(status_code=422, content=packet.to_wire())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and exc.detail.get("kind") == "error":
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        sid = request.headers.get("x-zen-session")
        seq = request.app.state.zen.sessions.next_seq(sid)
        code = "not_found" if exc.status_code == 404 else "http_error"
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        packet = make_error(code, str(message), sid=sid, seq=seq)
        return JSONResponse(status_code=exc.status_code, content=packet.to_wire())

    app.include_router(health_router)
    app.include_router(meta_router)
    app.include_router(session_router)
    _include_optional_routers(app)
    return app


def _include_optional_routers(app: FastAPI) -> None:
    """Attach resource routers if they have been implemented."""
    try:
        from zen.api.routers.agents import router as agents_router

        app.include_router(agents_router)
    except ImportError:
        pass
    try:
        from zen.api.routers.dex import router as dex_router

        app.include_router(dex_router)
    except ImportError:
        pass
    try:
        from zen.api.routers.plugins import router as plugins_router

        app.include_router(plugins_router)
    except ImportError:
        pass
    try:
        from zen.api.routers.inbox import router as inbox_router

        app.include_router(inbox_router)
    except ImportError:
        pass
    try:
        from zen.api.routers.chat import router as chat_router

        app.include_router(chat_router)
    except ImportError:
        pass
