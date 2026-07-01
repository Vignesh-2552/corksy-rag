from pydantic import BaseModel


class UploadResponse(BaseModel):
    status: str
    files: list[str]
    chunks: int


class SourceReference(BaseModel):
    doc_id: str
    source_file: str
    score: float
    snippet: str


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
    session_id: str
