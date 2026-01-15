import os
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from models.chat import ChatRequest, ChatResponse, Source
from services import rag_service

# Initialize OpenAI client
client = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Warning: OpenAI client initialization failed: {e}")

# System prompt - strictly document-based responses only
SYSTEM_PROMPT = """You are an AI assistant for Draco Cheng's personal portfolio website.

CRITICAL RULES:
1. ONLY answer based on the provided document context. Do NOT use any external knowledge about Draco.
2. If the information is not in the provided documents, say "I don't have that information in my documents."
3. Never guess, infer, or assume any facts not explicitly stated in the documents.
4. Do not make up experiences, skills, projects, or any personal details.

Style:
- Be helpful and professional
- Keep responses concise
- If relevant, suggest the visitor explore the website for more information
"""

api_router = APIRouter(prefix="")

@api_router.get("/ping")
def ping():
    """
    Simple health check endpoint for frontend-backend integration.
    """
    return {"result": "pong"}

@api_router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint with RAG support.

    Supports two modes:
    1. RAG mode (use_rag=True, default): Searches uploaded documents and uses them as context
    2. Direct mode (use_rag=False): Uses only the system prompt without document search

    Accepts a user message and optional conversation history.
    Returns an AI response with optional source citations.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    if not client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI service is not available. Please configure OPENAI_API_KEY."
        )

    try:
        # Check if RAG should be used
        print(f"[DEBUG] use_rag: {request.use_rag}")
        if request.use_rag:
            # Check if documents exist
            has_docs = await rag_service.has_documents()
            print(f"[DEBUG] has_documents: {has_docs}")

            if has_docs:
                # Use RAG mode
                print(f"[DEBUG] Using RAG mode for query: {request.message[:50]}...")
                response_text, sources = await rag_service.generate_rag_response(
                    query=request.message,
                    history=request.history,
                    system_prompt=SYSTEM_PROMPT
                )
                print(f"[DEBUG] RAG returned {len(sources)} sources")

                # Convert sources to Source models
                source_objects = [
                    Source(
                        document_id=src["document_id"],
                        filename=src["filename"],
                        content=src["content"],
                        score=src["score"]
                    )
                    for src in sources
                ]

                return ChatResponse(response=response_text, sources=source_objects)
            else:
                # No documents available - return helpful message instead of hallucinating
                print("No documents found, returning unavailable message")
                return ChatResponse(
                    response="Sorry, I'm unable to access the document database at the moment. Please try again later, or feel free to browse the website to learn more about Draco's experience and projects.",
                    sources=[]
                )

        # Direct mode (no RAG) - only used when use_rag=False is explicitly set
        # Build messages array for OpenAI
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history
        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current user message
        messages.append({"role": "user", "content": request.message})

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        assistant_message = response.choices[0].message.content

        return ChatResponse(response=assistant_message, sources=[])

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with OpenAI: {str(e)}"
        )
