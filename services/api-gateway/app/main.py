from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.router import router, story_proxy


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await story_proxy.aclose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DOCS_ENABLED else None,
    )


    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(router)

    @app.get("/health", tags=["healthcheck"])
    async def health():
        return {"status": "ok", "service": settings.APP_TITLE}

    return app


app = create_app()
