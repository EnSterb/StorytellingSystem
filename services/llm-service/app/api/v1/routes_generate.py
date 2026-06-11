from fastapi import APIRouter, Depends, HTTPException, status
from dependency_injector.wiring import inject, Provide

from app.containers import Container
from app.schemas import GenerateRequest, GenerateResponse
from app.services.generation import GenerationService

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("", response_model=GenerateResponse)
@inject
async def generate(
    body: GenerateRequest,
    service: GenerationService = Depends(Provide[Container.generation_service]),
) -> GenerateResponse:
    if not body.history and not body.system_prompt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Prompt cannot be empty",
        )
    text = await service.generate(
        system_prompt=body.system_prompt,
        history=[m.model_dump() for m in body.history],
    )
    return GenerateResponse(text=text)

