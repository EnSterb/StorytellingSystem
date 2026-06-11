from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.containers import Container
from app.core.db import get_db_session
from app.schemas import IngestRequest, IngestResponse
from app.services.ingestion import IngestionService
from app.repositories.chunk_repository import ChunkRepository

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
@inject
async def ingest_document(
    body: IngestRequest,
    session: AsyncSession = Depends(get_db_session),
    embedding_model=Depends(Provide[Container.embedding_model]),
) -> IngestResponse:
    if not body.content.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Content cannot be empty",
        )
    repo = ChunkRepository(session)
    service = IngestionService(repo=repo, embedding_model=embedding_model)
    chunks_created = await service.ingest_document(
        document_id=body.document_id,
        world_id=body.world_id,
        user_id=body.user_id,
        doc_type=body.doc_type,
        content=body.content,
    )
    return IngestResponse(document_id=body.document_id, chunks_created=chunks_created)

@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    repo = ChunkRepository(session)
    await repo.delete_by_document(document_id)
