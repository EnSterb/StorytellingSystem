from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.containers import Container
from app.api.v1 import router
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализируем контейнер и сразу прогреваем модель
    container = app.state.container
    container.embedding_model()  # ← вызов Singleton = загрузка модели
    print(f"Embedding model '{settings.EMBEDDING_MODEL}' loaded")
    yield
    print("Shutting down...")


def create_app() -> FastAPI:
    container = Container()

    app = FastAPI(
        title=settings.APP_TITLE,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DOCS_ENABLED else None,
    )

    app.state.container = container
    container.wire()   # связывает @inject в роутах с контейнером
    app.include_router(router)

    return app


app = create_app()
