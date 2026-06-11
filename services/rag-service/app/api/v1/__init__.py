from fastapi import APIRouter
from .routes_ingest import router as ingest_router
from .routes_retrieve import router as retrieve_router

router = APIRouter(prefix="/api/v1")
router.include_router(ingest_router)
router.include_router(retrieve_router)
