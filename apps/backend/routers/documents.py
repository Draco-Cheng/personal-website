"""
Documents API router.
Handles document upload, listing, and deletion endpoints.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Header
from typing import List, Optional
import config

from services import document_service, vector_store
from models.document import (
    DocumentUploadResponse,
    DocumentListItem,
    DocumentDeleteResponse
)

router = APIRouter(prefix="/admin/documents", tags=["documents"])


def verify_admin_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify admin API key for protected endpoints.

    Args:
        x_api_key: API key from X-API-Key header

    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not config.settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Admin API key not configured on server"
        )

    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header"
        )

    if x_api_key != config.settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )

    return True


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    x_api_key: Optional[str] = Header(None)
):
    """
    Upload and process a document (Admin only).

    Requires X-API-Key header for authentication.

    Supported file types: PDF, DOCX, XLSX, Markdown, TXT

    Steps:
    1. Validate file type and size
    2. Parse and extract text
    3. Chunk text into manageable pieces
    4. Generate embeddings using OpenAI
    5. Store in MongoDB Atlas

    Returns:
        DocumentUploadResponse with document ID and status
    """
    verify_admin_key(x_api_key)
    return await document_service.upload_document(file)


@router.get("", response_model=List[DocumentListItem])
async def list_documents():
    """
    List all uploaded documents.

    Returns:
        List of documents with metadata (filename, upload date, chunk count)
    """
    return await document_service.list_documents()


@router.get("/{document_id}")
async def get_document(document_id: str):
    """
    Get detailed information about a specific document.

    Args:
        document_id: Unique document identifier

    Returns:
        Document metadata and statistics
    """
    return await document_service.get_document_info(document_id)


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    x_api_key: Optional[str] = Header(None)
):
    """
    Delete a document and all its chunks (Admin only).

    Requires X-API-Key header for authentication.

    Args:
        document_id: Unique document identifier

    Returns:
        DocumentDeleteResponse with deletion status
    """
    verify_admin_key(x_api_key)
    return await document_service.delete_document(document_id)


@router.get("/stats/storage")
async def get_storage_stats():
    """
    Get storage statistics.

    Returns:
        Storage usage information (total documents, chunks, etc.)
    """
    return await vector_store.get_storage_stats()
