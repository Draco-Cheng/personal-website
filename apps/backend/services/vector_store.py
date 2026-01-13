"""
Vector store service for MongoDB Atlas Vector Search.
Handles storage and retrieval of document embeddings.
"""

from typing import List, Dict, Optional
import config

async def get_collection():
    """Get the MongoDB collection for documents"""
    if not config.mongodb_client:
        raise Exception("MongoDB client not initialized")

    db = config.mongodb_client[config.settings.MONGODB_DB_NAME]
    return db[config.settings.MONGODB_COLLECTION]


async def insert_chunks(chunks: List[Dict]) -> List[str]:
    """
    Insert document chunks with embeddings into MongoDB.

    Args:
        chunks: List of chunk dictionaries containing content, embedding, metadata

    Returns:
        List of inserted document IDs
    """
    collection = await get_collection()
    result = await collection.insert_many(chunks)
    return [str(id) for id in result.inserted_ids]


async def vector_search(query_embedding: List[float], top_k: int = 5, score_threshold: float = 0.7) -> List[Dict]:
    """
    Perform vector similarity search using MongoDB Atlas Vector Search.

    Args:
        query_embedding: The query vector (1536 dimensions for OpenAI embeddings)
        top_k: Number of results to return
        score_threshold: Minimum similarity score (0-1)

    Returns:
        List of matching chunks with scores
    """
    collection = await get_collection()

    pipeline = [
        {
            "$vectorSearch": {
                "index": config.settings.VECTOR_INDEX_NAME,
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": top_k * 10,  # Search more candidates for better results
                "limit": top_k
            }
        },
        {
            "$project": {
                "_id": 1,
                "filename": 1,
                "content": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = await collection.aggregate(pipeline).to_list(length=top_k)

    # Filter by score threshold
    filtered_results = [
        result for result in results
        if result.get("score", 0) >= score_threshold
    ]

    return filtered_results


async def list_all_documents() -> List[Dict]:
    """
    List all unique documents (grouped by document_id).

    Returns:
        List of document summaries
    """
    collection = await get_collection()

    pipeline = [
        {
            "$group": {
                "_id": "$metadata.document_id",
                "filename": {"$first": "$filename"},
                "upload_date": {"$first": "$metadata.upload_date"},
                "file_type": {"$first": "$metadata.file_type"},
                "chunk_count": {"$sum": 1}
            }
        },
        {
            "$project": {
                "id": "$_id",
                "filename": 1,
                "upload_date": 1,
                "file_type": 1,
                "chunk_count": 1,
                "_id": 0
            }
        },
        {
            "$sort": {"upload_date": -1}
        }
    ]

    results = await collection.aggregate(pipeline).to_list(length=None)
    return results


async def delete_document(document_id: str) -> int:
    """
    Delete all chunks of a document.

    Args:
        document_id: The unique document ID

    Returns:
        Number of chunks deleted
    """
    collection = await get_collection()

    result = await collection.delete_many({
        "metadata.document_id": document_id
    })

    return result.deleted_count


async def get_document_by_id(document_id: str) -> Optional[Dict]:
    """
    Get document metadata by ID.

    Args:
        document_id: The unique document ID

    Returns:
        Document metadata or None if not found
    """
    collection = await get_collection()

    # Get the first chunk to retrieve metadata
    chunk = await collection.find_one({
        "metadata.document_id": document_id
    })

    if not chunk:
        return None

    # Count total chunks
    chunk_count = await collection.count_documents({
        "metadata.document_id": document_id
    })

    return {
        "id": document_id,
        "filename": chunk.get("filename"),
        "upload_date": chunk.get("metadata", {}).get("upload_date"),
        "file_type": chunk.get("metadata", {}).get("file_type"),
        "chunk_count": chunk_count
    }


async def get_storage_stats() -> Dict:
    """
    Get storage statistics for monitoring.

    Returns:
        Dictionary with storage stats
    """
    collection = await get_collection()

    total_chunks = await collection.count_documents({})

    # Get unique document count
    pipeline = [
        {
            "$group": {
                "_id": "$metadata.document_id"
            }
        },
        {
            "$count": "total_documents"
        }
    ]

    doc_count_result = await collection.aggregate(pipeline).to_list(length=1)
    total_documents = doc_count_result[0]["total_documents"] if doc_count_result else 0

    return {
        "total_documents": total_documents,
        "total_chunks": total_chunks,
        "avg_chunks_per_document": round(total_chunks / total_documents, 2) if total_documents > 0 else 0
    }
