"""
Documents API router.
Handles document upload, listing, and deletion endpoints.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Header, Depends
from typing import List, Optional
import config

from services import document_service, vector_store
from models.document import (
    DocumentUploadResponse,
    DocumentListItem,
    DocumentDeleteResponse
)


def verify_admin_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify admin API key for protected endpoints.
    Used as a dependency for all admin routes.
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


# All routes in this router require admin API key
router = APIRouter(
    prefix="/admin/documents",
    tags=["documents"],
    dependencies=[Depends(verify_admin_key)]
)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document.

    Supported file types: PDF, DOCX, XLSX, Markdown, TXT

    Returns:
        DocumentUploadResponse with document ID and status
    """
    return await document_service.upload_document(file)


@router.get("", response_model=List[DocumentListItem])
async def list_documents():
    """
    List all uploaded documents.

    Returns:
        List of documents with metadata (filename, upload date, chunk count)
    """
    return await document_service.list_documents()


@router.get("/stats/storage")
async def get_storage_stats():
    """
    Get storage statistics.

    Returns:
        Storage usage information (total documents, chunks, etc.)
    """
    return await vector_store.get_storage_stats()


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
async def delete_document(document_id: str):
    """
    Delete a document and all its chunks.

    Args:
        document_id: Unique document identifier

    Returns:
        DocumentDeleteResponse with deletion status
    """
    return await document_service.delete_document(document_id)
