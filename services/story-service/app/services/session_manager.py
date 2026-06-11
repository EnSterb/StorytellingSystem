from fastapi import HTTPException, status

from app.models.session import Session, SessionModeEnum
from app.models.message import RoleEnum
from app.repositories.session_repository import SessionRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.world_repository import WorldRepository


class SessionManager:

    def __init__(
        self,
        session_repository: SessionRepository,
        message_repository: MessageRepository,
        world_repository: WorldRepository,
    ) -> None:
        self._session_repo = session_repository
        self._message_repo = message_repository
        self._world_repo = world_repository

    async def create_session(
            self,
            user_id: int,
            title: str | None = None,
            world_id: int | None = None,
            mode: SessionModeEnum = SessionModeEnum.narrator,
            character_name: str | None = None,
    ) -> Session:
        if world_id:
            world = await self._world_repo.get_by_id(world_id)
            if not world or world.owner_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="World not found",
                )
        return await self._session_repo.create(
            user_id=user_id,
            title=title,
            world_id=world_id,
            mode=mode,
            character_name=character_name,
        )

    async def get_session(self, session_id: int, user_id: int) -> Session:
        session = await self._session_repo.get_by_id(session_id)
        if not session or session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        return session

    async def get_user_sessions(
            self, user_id: int, limit: int = 20, offset: int = 0
    ) -> tuple[list[Session], int]:
        items = await self._session_repo.get_by_user_id(user_id, limit=limit, offset=offset)
        total = await self._session_repo.count_by_user(user_id)
        return items, total

    async def delete_session(self, session_id: int, user_id: int) -> None:
        session = await self.get_session(session_id, user_id)
        await self._session_repo.delete(session.id)

    async def count_messages(self, session_id: int) -> int:
        return await self._message_repo.count_by_session(session_id)

    async def append_message(self, session_id, user_id, role, content,
                             used_chunks: str | None = None):
        await self.get_session(session_id, user_id)
        return await self._message_repo.create(
            session_id=session_id, role=role, content=content,
            used_chunks=used_chunks,
        )

    async def get_history(
        self,
        session_id: int,
        user_id: int,
        last_n: int | None = None,
    ):
        await self.get_session(session_id, user_id)
        if last_n:
            return await self._message_repo.get_last_n(session_id, last_n)
        return await self._message_repo.get_by_session_id(session_id)

    async def update_summary(
        self,
        session_id: int,
        user_id: int,
        summary: str,
    ) -> Session:
        await self.get_session(session_id, user_id)
        return await self._session_repo.update_summary(session_id, summary)

    async def get_world_sessions(
            self, world_id: int, user_id: int, limit: int = 100, offset: int = 0
    ) -> tuple[list[Session], int]:
        # Проверяем что мир существует и принадлежит юзеру
        world = await self._world_repo.get_by_id(world_id)
        if not world or world.owner_id != user_id:
            raise HTTPException(status_code=404, detail="World not found")
        items = await self._session_repo.get_by_world_id(world_id, user_id, limit, offset)
        total = await self._session_repo.count_by_world(world_id, user_id)
        return items, total
