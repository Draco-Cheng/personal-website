import os
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()

# Initialize OpenAI client
client = None
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Warning: OpenAI client initialization failed: {e}")

@app.get("/")
@app.head("/")
def health_check():
    """
    Health check endpoint for monitoring and CI/CD.
    Supports both GET and HEAD methods for wait-on compatibility.
    """
    return {"status": "ok", "service": "backend"}

# Request and response models for chat endpoint
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str

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
def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint for OpenAI integration.
    Accepts a user message and optional conversation history.
    Returns an AI response based on Draco's profile information.
    """
    if not client:
        raise HTTPException(
            status_code=503,
            detail="OpenAI service is not available. Please configure OPENAI_API_KEY."
        )

    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    try:
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

        return ChatResponse(response=assistant_message)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with OpenAI: {str(e)}"
        )

# Include the API router
app.include_router(api_router)