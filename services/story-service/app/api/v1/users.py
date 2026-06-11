from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas import UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    repo = UserRepository(session)

    # Проверяем уникальность нового username
    if body.username and body.username != current_user.username:
        existing = await repo.get_by_username(body.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

    # Проверяем уникальность нового email
    if body.email and body.email != current_user.email:
        if await repo.exists_by_email(body.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    updates = body.model_dump(exclude_none=True)
    if not updates:
        return current_user

    updated = await repo.update(current_user.id, **updates)
    return updated


@router.delete("/me", status_code=204)
async def delete_me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
):
    await UserRepository(session).delete(current_user.id)
