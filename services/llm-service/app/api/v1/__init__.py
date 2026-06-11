from fastapi import APIRouter
from .routes_generate import router as generate_router

router = APIRouter(prefix="/api/v1")
router.include_router(generate_router)
