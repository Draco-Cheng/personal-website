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

About Draco Cheng:
- Role: Senior Software Engineer & Product Architect
- Experience: 12+ years shipping products
- Projects launched: 12
- Mentored engineers: 5

Work Experience:
1. Senior Software Developer at Trend Micro (2019-2025)
   - Scaled a cross-region monorepo platform spanning React, Node, and Pulumi
   - Drove AI-assisted delivery and mentored four engineers
   - Embedded Nx + Cypress patterns into large Angular initiatives

2. Senior Software Developer at London Stock Exchange Group / Yield Book (2018-2019)
   - Led frontend work for fixed-income analytics
   - Automated reporting with BIRT
   - Shipped internal tooling for server telemetry

3. Senior Software Developer at Isentia (2017)
   - Rebuilt internal admin and demo apps with refreshed UX patterns
   - Added rapid customization paths for enterprise media clients

4. Software Developer at Elastic Grid (2016-2017)
   - Delivered multilingual campaign microsites and EDM systems
   - Worked with clients like NetApp, Juniper, Atlassian, and Veritas

5. Software Developer at Ubitus (2012-2016)
   - Built secure middleware and Ember.js web apps
   - Powered cloud gaming across Xbox One, Samsung, and major telecom ecosystems

Key Projects:
1. Mono Repo Skeleton
   - Nx-powered template with Next.js 15 frontend and FastAPI backend
   - Includes Docker, Helm charts, and CI-ready testing presets
   - GitHub: https://github.com/Draco-Cheng/mono-repo-skeleton

2. AI_README MCP Server
   - Model Context Protocol server for AI coding assistants
   - Discovers, routes, and validates AI_README guides
   - Helps copilots follow team conventions by default
   - GitHub: https://github.com/Draco-Cheng/ai-readme-mcp

Technical Skills:
- Frontend: React, Next.js, Angular, Ember.js, TypeScript
- Backend: Node.js, Python, FastAPI
- Tools: Nx, Pulumi, Cypress, Docker, Kubernetes
- Architecture: Monorepo, Microservices, Cloud Gaming

Instructions:
- Be helpful, professional, and enthusiastic
- Answer questions about Draco's experience, skills, and projects
- Guide visitors to relevant parts of the portfolio
- If asked about something not in your knowledge, politely say you don't have that information
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
        if request.use_rag:
            # Check if documents exist
            has_docs = await rag_service.has_documents()

            if has_docs:
                # Use RAG mode
                response_text, sources = await rag_service.generate_rag_response(
                    query=request.message,
                    history=request.history,
                    system_prompt=SYSTEM_PROMPT
                )

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
