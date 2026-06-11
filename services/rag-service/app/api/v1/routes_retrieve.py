from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.containers import Container
from app.core.db import get_db_session
from app.schemas import RetrieveRequest, RetrieveResponse
from app.services.retriever import RetrieverService
from app.services.prompt_builder import PromptBuilder
from app.repositories.chunk_repository import ChunkRepository

router = APIRouter(prefix="/retrieve-context", tags=["retrieve"])


@router.post("", response_model=RetrieveResponse)
@inject
async def retrieve_context(
    body: RetrieveRequest,
    session: AsyncSession = Depends(get_db_session),
    embedding_model=Depends(Provide[Container.embedding_model]),
    prompt_builder: PromptBuilder = Depends(Provide[Container.prompt_builder]),
) -> RetrieveResponse:
    repo = ChunkRepository(session)
    retriever = RetrieverService(repo=repo, embedding_model=embedding_model)
    chunks = await retriever.retrieve(
        query=body.query,
        world_id=body.world_id,
        top_k=body.top_k,
    )
    system_prompt = prompt_builder.build(query=body.query, chunks=chunks)
    return RetrieveResponse(
        prompt=system_prompt,
        chunks_found=len(chunks),
        chunk_ids=[c.id for c in chunks],
    )
