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

# System prompt with profile information
SYSTEM_PROMPT = """You are an AI assistant for Draco Cheng's personal portfolio website. Your role is to help visitors learn about Draco's professional experience, skills, and projects.

Instructions:
- Be helpful, professional, and enthusiastic
- Answer questions about Draco's professional experience, skills, projects, and personal information
- Use information from uploaded documents to answer questions about personal details (e.g., visa status, certifications, etc.)
- Guide visitors to relevant parts of the portfolio
- CRITICAL: Only state facts that are explicitly mentioned in your knowledge or the provided information. Never infer, assume, or guess information.
- If asked about something not explicitly stated (like nationality, age, personal details not mentioned), politely say you don't have that specific information
- Don't make assumptions based on indirect clues (e.g., don't infer nationality from language skills or work location)
- Keep responses concise but informative
- Suggest exploring specific projects or experience areas when relevant
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
                # No documents available, fall back to direct mode
                print("No documents found, falling back to direct mode")

        # Direct mode (no RAG)
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
