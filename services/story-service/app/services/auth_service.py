import secrets
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status

from app.core.email import send_verification_email
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.repositories.revoked_token_repository import RevokedTokenRepository
from app.repositories.user_repository import UserRepository


class AuthService:

    def __init__(
        self,
        user_repository: UserRepository,
        revoked_token_repository: RevokedTokenRepository,
    ) -> None:
        self._user_repo = user_repository
        self._revoked_repo = revoked_token_repository

    async def register(self, username: str, email: str, password: str) -> User:
        if await self._user_repo.exists_by_email(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        verification_token = secrets.token_urlsafe(32)
        verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        user = await self._user_repo.create(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            verification_token=verification_token,
            verification_token_expires_at=verification_token_expires_at,
            is_active=False,
        )
        await send_verification_email(email=email, token=verification_token)
        return user

    async def verify_email(self, token: str) -> User:
        user = await self._user_repo.get_by_verification_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            )
        if user.verification_token_expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token has expired",
            )
        return await self._user_repo.activate(user)

    async def login(self, email: str, password: str) -> str:
        user = await self._user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Check your inbox.",
            )
        token, jti, expires_at = create_access_token(subject=user.id)
        return token

    async def logout(self, token_payload: dict) -> None:
        jti = token_payload["jti"]
        expires_at = datetime.fromtimestamp(token_payload["exp"], tz=timezone.utc)
        await self._revoked_repo.revoke(jti=jti, expires_at=expires_at)

    async def resend_verification(self, email: str) -> None:
        user = await self._user_repo.get_by_email(email)

        # Не раскрываем существует ли email
        if not user or user.is_active:
            return

        # Проверяем что токен ещё не просрочен
        if (
                user.verification_token_expires_at
                and user.verification_token_expires_at > datetime.now(timezone.utc)
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Verification email already sent. Check your inbox or wait before retrying.",
            )

        # Генерируем новый токен
        verification_token = secrets.token_urlsafe(32)
        verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

        await self._user_repo.update(
            user.id,
            verification_token=verification_token,
            verification_token_expires_at=verification_token_expires_at,
        )
        await send_verification_email(email=email, token=verification_token)
