from dependency_injector import containers, providers
from app.core.config import settings
from app.core.db import AsyncSessionFactory
from app.embeddings.model import EmbeddingModel
from app.repositories.chunk_repository import ChunkRepository
from app.services.ingestion import IngestionService
from app.services.retriever import RetrieverService
from app.services.prompt_builder import PromptBuilder
from app.core.db import get_db_session


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.routes_ingest",
            "app.api.v1.routes_retrieve",
        ]
    )

    embedding_model = providers.Singleton(EmbeddingModel)

    # Resource — управляет lifecycle сессии (commit/rollback/close)
    db_session = providers.Resource(get_db_session)

    chunk_repository = providers.Factory(
        ChunkRepository,
        session=db_session,
    )

    ingestion_service = providers.Factory(
        IngestionService,
        repo=chunk_repository,
        embedding_model=embedding_model,
    )

    retriever_service = providers.Factory(
        RetrieverService,
        repo=chunk_repository,
        embedding_model=embedding_model,
    )

    prompt_builder = providers.Singleton(PromptBuilder)
