from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., max_length=500)
    session_id: str
    top_k: int = Field(default=5, ge=1, le=20)
