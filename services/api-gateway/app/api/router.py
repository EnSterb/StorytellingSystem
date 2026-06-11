from fastapi import APIRouter, Depends, Request, Response
from app.core.dependencies import verify_token
from app.proxy.client import ProxyClient
from app.core.config import settings

router = APIRouter()

story_proxy = ProxyClient(settings.STORY_SERVICE_URL)

# Публичные маршруты — без проверки токена
PUBLIC_PREFIXES = [
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/verify",
]


@router.api_route(
    "/api/v1/auth/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
)
async def proxy_auth(path: str, request: Request) -> Response:
    return await story_proxy.forward(request, f"/api/v1/auth/{path}")


@router.api_route(
    "/api/v1/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    dependencies=[Depends(verify_token)],
)
async def proxy_protected(path: str, request: Request) -> Response:
    return await story_proxy.forward(request, f"/api/v1/{path}")
