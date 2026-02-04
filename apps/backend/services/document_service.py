"""
Document processing service.
Handles file upload, parsing, chunking, embedding, and storage.
"""

from typing import List, Dict
from fastapi import UploadFile, HTTPException
from datetime import datetime
import uuid

from langchain_text_splitters import RecursiveCharacterTextSplitter

import config
from utils import file_parser
from services import vector_store
from models.document import (
    DocumentUploadResponse,
    DocumentListItem,
    DocumentDeleteResponse
)

# File type whitelist
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "text/markdown",
    "text/plain",
}

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".md", ".markdown", ".txt"}


async def upload_document(file: UploadFile) -> DocumentUploadResponse:
    """
    Process and store an uploaded document.

    Steps:
    1. Validate file type and size
    2. Parse file content
    3. Clean and chunk text
    4. Generate embeddings
    5. Store in MongoDB

    Args:
        file: Uploaded file from FastAPI

    Returns:
        DocumentUploadResponse with upload status

    Raises:
        HTTPException: If validation or processing fails
    """
    if not config.openai_client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI service not available. Cannot process documents."
        )

    if not config.mongodb_client:
        raise HTTPException(
            status_code=503,
            detail="MongoDB not connected. Cannot store documents."
        )

    # Validate file type
    filename = file.filename or "unknown"
    file_ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    file_content = await file.read()

    # Validate file size
    max_size = config.settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {config.settings.MAX_FILE_SIZE_MB}MB"
        )

    if len(file_content) == 0:
        raise HTTPException(
            status_code=400,
            detail="File is empty"
        )

    try:
        # Step 1: Parse file
        raw_text = file_parser.parse_file(file_content, filename)
        cleaned_text = file_parser.clean_text(raw_text)

        if len(cleaned_text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="File contains insufficient text content"
            )

        # Step 2: Chunk text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.settings.CHUNK_SIZE,
            chunk_overlap=config.settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = text_splitter.split_text(cleaned_text)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="Text splitting resulted in no chunks"
            )

        # Step 3: Generate embeddings
        embeddings = await generate_embeddings([chunk for chunk in chunks])

        # Step 4: Prepare document chunks for storage
        document_id = str(uuid.uuid4())
        upload_date = datetime.utcnow().isoformat()
        file_type = file_ext.lstrip(".")

        chunks_to_insert = []
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_doc = {
                "filename": filename,
                "chunk_index": idx,
                "content": chunk_text,
                "embedding": embedding,
                "metadata": {
                    "upload_date": upload_date,
                    "file_type": file_type,
                    "total_chunks": len(chunks),
                    "document_id": document_id
                }
            }
            chunks_to_insert.append(chunk_doc)

        # Step 5: Insert into MongoDB
        await vector_store.insert_chunks(chunks_to_insert)

        return DocumentUploadResponse(
            id=document_id,
            filename=filename,
            status="success",
            chunk_count=len(chunks),
            message=f"Document processed into {len(chunks)} chunks"
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )


async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using OpenAI.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors
    """
    if not config.openai_client:
        raise Exception("OpenAI client not available")

    # Batch process embeddings (OpenAI allows up to 2048 inputs per request)
    batch_size = 100
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        response = config.openai_client.embeddings.create(
            input=batch,
            model=config.settings.EMBEDDING_MODEL
        )

        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


async def list_documents() -> List[DocumentListItem]:
    """
    List all uploaded documents.

    Returns:
        List of DocumentListItem
    """
    documents = await vector_store.list_all_documents()

    return [
        DocumentListItem(
            id=doc["id"],
            filename=doc["filename"],
            upload_date=doc["upload_date"],
            chunk_count=doc["chunk_count"],
            file_type=doc["file_type"]
        )
        for doc in documents
    ]


async def delete_document(document_id: str) -> DocumentDeleteResponse:
    """
    Delete a document and all its chunks.

    Args:
        document_id: Unique document ID

    Returns:
        DocumentDeleteResponse

    Raises:
        HTTPException: If document not found
    """
    # Check if document exists
    doc = await vector_store.get_document_by_id(document_id)
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )

    # Delete all chunks
    deleted_count = await vector_store.delete_document(document_id)

    return DocumentDeleteResponse(
        success=True,
        message=f"Document '{doc['filename']}' deleted successfully",
        deleted_chunks=deleted_count
    )


async def get_document_info(document_id: str) -> Dict:
    """
    Get detailed information about a document.

    Args:
        document_id: Unique document ID

    Returns:
        Document information dictionary

    Raises:
        HTTPException: If document not found
    """
    doc = await vector_store.get_document_by_id(document_id)

    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"Document {document_id} not found"
        )

    return doc
