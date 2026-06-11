from datetime import datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.revoked_token import RevokedToken
from app.repositories.base import BaseRepository


class RevokedTokenRepository(BaseRepository[RevokedToken]):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RevokedToken, session)

    async def revoke(self, jti: str, expires_at: datetime) -> None:
        token = RevokedToken(jti=jti, expires_at=expires_at)
        self._session.add(token)
        await self._session.flush()

    async def is_revoked(self, jti: str) -> bool:
        result = await self._session.execute(
            select(RevokedToken.id).where(RevokedToken.jti == jti)
        )
        return result.scalar_one_or_none() is not None

    async def cleanup_expired(self) -> None:
        """Чистим просроченные токены из таблицы"""
        await self._session.execute(
            delete(RevokedToken).where(
                RevokedToken.expires_at < datetime.now(timezone.utc)
            )
        )
        await self._session.flush()
