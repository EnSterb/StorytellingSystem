from pydantic import BaseModel


class RetrieveRequest(BaseModel):
    query: str
    world_id: int
    top_k: int = 5


class RetrieveResponse(BaseModel):
    prompt: str
    chunks_found: int
    chunk_ids: list[int] = []
