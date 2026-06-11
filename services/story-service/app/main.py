from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.containers import Container
container = Container()
container.wire(modules=[
    "app.api.v1.documents",
    "app.api.v1.auth",
    "app.api.v1.worlds",
    "app.api.v1.sessions",
    "app.api.v1.users",
])

from app.core.exceptions import register_exception_handlers
from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.worlds import router as worlds_router
from app.api.v1.sessions import router as sessions_router
from app.api.v1.users import router as users_router
from app.api.v1.documents import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.container = container
    yield
    await container.rag_client().aclose()
    await container.llm_client().aclose()
    from app.core.db import engine
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    register_exception_handlers(app)

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(worlds_router, prefix="/api/v1")
    app.include_router(sessions_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(documents_router, prefix="/api/v1")

    @app.get("/health", tags=["healthcheck"])
    async def health():
        return {"status": "ok", "service": settings.APP_TITLE}

    return app


app = create_app()
