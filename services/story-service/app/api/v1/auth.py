from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
import re
from pydantic import field_validator
from app.core.security import verify_password, hash_password

from app.core.db import get_db_session
from app.core.dependencies import get_current_user, oauth2_scheme
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.revoked_token_repository import RevokedTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas import (RegisterRequest,
                         LoginRequest,
                         TokenResponse,
                         UserResponse,
                         ChangePasswordRequest,
                         ResendVerificationRequest)
from app.services.auth_service import AuthService
from starlette import status

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service(session: AsyncSession = Depends(get_db_session)) -> AuthService:
    return AuthService(
        user_repository=UserRepository(session),
        revoked_token_repository=RevokedTokenRepository(session),
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    body: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):
    return await service.register(
        username=body.username,
        email=body.email,
        password=body.password,
    )


@router.get("/verify", response_model=UserResponse)
async def verify_email(
    token: str,
    service: AuthService = Depends(get_auth_service),
):
    return await service.verify_email(token)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    token = await service.login(email=body.email, password=body.password)
    return TokenResponse(access_token=token)


@router.post("/logout", status_code=204)
async def logout(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    payload = decode_access_token(token)
    await service.logout(token_payload=payload)


# Только для Swagger UI
@router.post("/login/swagger", response_model=TokenResponse, include_in_schema=False)
async def login_swagger(
    form: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    token = await service.login(email=form.username, password=form.password)
    return TokenResponse(access_token=token)

@router.post("/change-password", status_code=204)
async def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    if not verify_password(body.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect",
        )
    await UserRepository(session).update(
        current_user.id,
        hashed_password=hash_password(body.new_password),
    )


@router.post("/resend-verification", status_code=204)
async def resend_verification(
    body: ResendVerificationRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.resend_verification(email=body.email)
