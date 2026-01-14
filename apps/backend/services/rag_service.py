"""
RAG (Retrieval-Augmented Generation) service.
Handles vector search, prompt building, and response generation.
"""

from typing import List, Tuple, Dict
import os
from openai import OpenAI

import config
from services import vector_store
from models.chat import ChatMessage

# Initialize OpenAI client
openai_client = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        openai_client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Warning: OpenAI client initialization failed in rag_service: {e}")


async def retrieve_relevant_chunks(query: str, top_k: int = 5, score_threshold: float = 0.5) -> List[Dict]:
    """
    Retrieve relevant document chunks for a query using vector search.

    Args:
        query: User's question
        top_k: Number of chunks to retrieve
        score_threshold: Minimum similarity score (0-1)

    Returns:
        List of relevant chunks with scores
    """
    if not openai_client:
        raise Exception("OpenAI client not available")

    # Generate embedding for the query
    response = openai_client.embeddings.create(
        input=[query],
        model=config.settings.EMBEDDING_MODEL
    )

    query_embedding = response.data[0].embedding

    # Perform vector search
    results = await vector_store.vector_search(
        query_embedding=query_embedding,
        top_k=top_k,
        score_threshold=score_threshold
    )

    print(f"[DEBUG] Vector search returned {len(results)} chunks for query: {query[:50]}...")
    for i, result in enumerate(results[:3]):  # Print first 3 results
        print(f"[DEBUG]   Chunk {i+1}: {result.get('filename')} (score: {result.get('score', 0):.3f})")

    return results


def build_rag_prompt(system_prompt: str, query: str, chunks: List[Dict]) -> List[Dict]:
    """
    Build a prompt that includes retrieved context.

    Args:
        system_prompt: Base system prompt
        query: User's question
        chunks: Retrieved document chunks

    Returns:
        List of message dictionaries for OpenAI API
    """
    messages = [{"role": "system", "content": system_prompt}]

    # Add retrieved context as system message
    if chunks:
        context_parts = []
        for chunk in chunks:
            content = chunk.get("content", "")
            context_parts.append(content)

        context_message = (
            "Here is information about Draco:\n\n" +
            "\n\n".join(context_parts) +
            "\n\n---\n\nAnswer the user's question naturally and conversationally based ONLY on the above information. "
            "Don't mention 'documents', 'files', or 'provided information'. "
            "IMPORTANT: Only state facts explicitly mentioned above. Don't infer or assume additional details. "
            "If the information doesn't contain the answer, say you don't have that specific information."
        )

        messages.append({"role": "system", "content": context_message})

    # Add user query
    messages.append({"role": "user", "content": query})

    return messages


async def generate_rag_response(
    query: str,
    history: List[ChatMessage],
    system_prompt: str
) -> Tuple[str, List[Dict]]:
    """
    Generate a response using RAG (Retrieval-Augmented Generation).

    Steps:
    1. Retrieve relevant chunks from vector store
    2. Build prompt with context
    3. Call GPT to generate response
    4. Return response and sources

    Args:
        query: User's question
        history: Conversation history
        system_prompt: Base system prompt

    Returns:
        Tuple of (response_text, sources)
    """
    if not openai_client:
        raise Exception("OpenAI client not available")

    # Step 1: Retrieve relevant chunks
    chunks = await retrieve_relevant_chunks(query, top_k=5, score_threshold=0.5)

    # Step 2: Build prompt with context
    messages = build_rag_prompt(system_prompt, query, chunks)

    # Add conversation history before the current query
    # Insert history after system messages but before current query
    if history:
        history_messages = []
        for msg in history:
            history_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        # Insert history before the last message (current query)
        messages = messages[:-1] + history_messages + [messages[-1]]

    # Step 3: Call GPT
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    assistant_message = response.choices[0].message.content

    # Step 4: Format sources
    sources = []
    for chunk in chunks:
        sources.append({
            "document_id": chunk.get("metadata", {}).get("document_id", ""),
            "filename": chunk.get("filename", "Unknown"),
            "content": chunk.get("content", "")[:200] + "...",  # Preview only
            "score": chunk.get("score", 0)
        })

    return assistant_message, sources


async def has_documents() -> bool:
    """
    Check if there are any documents in the vector store.

    Returns:
        True if documents exist, False otherwise
    """
    try:
        stats = await vector_store.get_storage_stats()
        return stats.get("total_documents", 0) > 0
    except Exception:
        return False
