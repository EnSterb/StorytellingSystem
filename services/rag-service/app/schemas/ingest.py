from pydantic import BaseModel


class IngestRequest(BaseModel):
    document_id: int
    world_id: int
    user_id: int
    doc_type: str
    content: str


class IngestResponse(BaseModel):
    document_id: int
    chunks_created: int
