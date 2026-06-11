from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.containers import Container
from app.api.v1 import router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = app.state.container
    # Прогреваем клиент — просто инициализируем Singleton
    container.llm_backend()
    print(f"LLM backend ready → {settings.LLM_BASE_URL} | model: {settings.LLM_MODEL}")
    yield
    print("Shutting down LLM service...")


def create_app() -> FastAPI:
    container = Container()

    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DOCS_ENABLED else None,
    )

    app.state.container = container
    container.wire()
    app.include_router(router)

    return app


app = create_app()
