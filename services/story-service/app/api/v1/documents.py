from fastapi import APIRouter, Depends, Query, Path
from dependency_injector.wiring import inject, Provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.containers import Container
from app.clients.rag_client import RagClient
from app.core.db import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.repositories.world_repository import WorldRepository
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentResponse
from app.schemas.pagination import PageResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/worlds/{world_id}/documents", tags=["documents"])


@inject
def get_document_service(
    world_id: int = Path(...),
    session: AsyncSession = Depends(get_db_session),
    rag_client: RagClient = Depends(Provide[Container.rag_client]),
) -> DocumentService:
    return DocumentService(
        document_repository=DocumentRepository(session),
        world_repository=WorldRepository(session),
        rag_client=rag_client,
    )


@router.post("", response_model=DocumentResponse, status_code=201, operation_id="create_document")
async def create_document(
    world_id: int = Path(...),
    body: DocumentCreate = ...,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    document = await service.create_document(
        world_id=world_id,
        user_id=current_user.id,
        title=body.title,
        content=body.content,
        doc_type=body.doc_type,
    )
    return DocumentResponse.model_validate(document)


@router.get("", response_model=PageResponse[DocumentResponse], operation_id="list_documents")
async def get_documents(
    world_id: int = Path(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    items, total = await service.get_documents(
        world_id, current_user.id, limit=limit, offset=offset
    )
    return PageResponse(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/unindexed",
    response_model=list[DocumentResponse],
)
async def get_unindexed_documents(
    world_id: int,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    return await service.get_unindexed(world_id, current_user.id)


@router.get("/{document_id}", response_model=DocumentResponse, operation_id="get_document")
async def get_document(
    world_id: int = Path(...),
    document_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    return await service.get_document(world_id, document_id, current_user.id)


@router.patch("/{document_id}", response_model=DocumentResponse, operation_id="update_document")
async def update_document(
    world_id: int = Path(...),
    document_id: int = Path(...),
    body: DocumentUpdate = ...,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    updates = body.model_dump(exclude_none=True)
    return await service.update_document(
        world_id=world_id,
        document_id=document_id,
        user_id=current_user.id,
        **updates,
    )


@router.delete("/{document_id}", status_code=204, operation_id="delete_document")
async def delete_document(
    world_id: int = Path(...),
    document_id: int = Path(...),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    await service.delete_document(world_id, document_id, current_user.id)
