from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.clients.rag_client import RagClient
from app.clients.llm_client import LLMClient
from app.services.chat_service import ChatService
from app.schemas import ChatRequest, ChatResponse

from app.core.db import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.world_repository import WorldRepository
from app.schemas import (
    SessionCreate,
    SessionResponse,
    MessageResponse,
    MessageCreate,
    PageResponse,
)
from app.services.session_manager import SessionManager


router = APIRouter(prefix="/worlds/{world_id}/sessions", tags=["sessions"])


def get_session_manager(
    db: AsyncSession = Depends(get_db_session),
) -> SessionManager:
    return SessionManager(
        session_repository=SessionRepository(db),
        message_repository=MessageRepository(db),
        world_repository=WorldRepository(db),
    )



@router.get("", response_model=PageResponse[SessionResponse])
async def get_sessions(
    world_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    manager: SessionManager = Depends(get_session_manager),
):
    items, total = await manager.get_world_sessions(
        world_id=world_id,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return PageResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    world_id: int,            # берётся из пути, сейчас можно не использовать
    session_id: int,
    current_user: User = Depends(get_current_user),
    manager: SessionManager = Depends(get_session_manager),
):
    return await manager.get_session(session_id, current_user.id)


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    world_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    manager: SessionManager = Depends(get_session_manager),
):
    await manager.delete_session(session_id, current_user.id)


@router.get("/{session_id}/history", response_model=list[MessageResponse])
async def get_history(
    world_id: int,
    session_id: int,
    last_n: int | None = None,
    current_user: User = Depends(get_current_user),
    manager: SessionManager = Depends(get_session_manager),
):
    return await manager.get_history(session_id, current_user.id, last_n)


@router.post("/{session_id}/messages", response_model=MessageResponse, status_code=201)
async def append_message(
    world_id: int,
    session_id: int,
    body: MessageCreate,
    current_user: User = Depends(get_current_user),
    manager: SessionManager = Depends(get_session_manager),
):
    return await manager.append_message(
        session_id=session_id,
        user_id=current_user.id,
        role=body.role,
        content=body.content,
    )


@inject
def get_chat_service(
    db: AsyncSession = Depends(get_db_session),
    rag_client: RagClient = Depends(Provide[Container.rag_client]),
    llm_client: LLMClient = Depends(Provide[Container.llm_client]),
) -> ChatService:
    return ChatService(
        session_manager=SessionManager(
            session_repository=SessionRepository(db),
            message_repository=MessageRepository(db),
            world_repository=WorldRepository(db),
        ),
        rag_client=rag_client,
        llm_client=llm_client,
    )


@router.post("/{session_id}/chat", response_model=ChatResponse)
async def chat(
    world_id: int,
    session_id: int,
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    answer = await service.chat(
        session_id=session_id,
        user_id=current_user.id,
        user_message=body.message,
    )
    return ChatResponse(answer=answer)

@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    world_id: int,
    body: SessionCreate,
    current_user: User = Depends(get_current_user),
    manager: SessionManager = Depends(get_session_manager),
    service: ChatService = Depends(get_chat_service),
):
    session = await manager.create_session(
        user_id=current_user.id,
        title=body.title,
        world_id=world_id,
        mode=body.mode,
        character_name=body.character_name,
    )

    if body.generate_intro:
        await service.generate_intro(session_id=session.id, user_id=current_user.id)

    return session
