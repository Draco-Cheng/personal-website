from pydantic import BaseModel
from typing import Optional

class DocumentMetadata(BaseModel):
    """Metadata for a document chunk"""
    upload_date: str
    file_type: str
    total_chunks: int
    document_id: str

class DocumentChunk(BaseModel):
    """A single chunk of a document with its embedding"""
    filename: str
    chunk_index: int
    content: str
    embedding: Optional[list[float]] = None
    metadata: DocumentMetadata

class DocumentUploadResponse(BaseModel):
    """Response after uploading a document"""
    id: str
    filename: str
    status: str
    chunk_count: int
    message: Optional[str] = None

class DocumentListItem(BaseModel):
    """Summary information about a document"""
    id: str
    filename: str
    upload_date: str
    chunk_count: int
    file_type: str

class DocumentDeleteResponse(BaseModel):
    """Response after deleting a document"""
    success: bool
    message: str
    deleted_chunks: int
