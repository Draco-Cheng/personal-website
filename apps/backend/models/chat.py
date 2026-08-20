
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str

class Source(BaseModel):
    """Source document for RAG responses"""
    document_id: str
    filename: str
    content: str
    score: float

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    use_rag: bool = True  # Enable RAG by default

class ChatResponse(BaseModel):
    response: str
    sources: list[Source] = []  # RAG sources (empty if RAG not used)
