from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import config
from routers import chat, documents

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup: Connect to MongoDB
    if config.settings.MONGODB_URI:
        try:
            # Configure TLS options for OpenSSL 3.x compatibility with MongoDB Atlas
            import ssl

            # Create SSL context with relaxed security for MongoDB Atlas
            ssl_context = ssl.create_default_context()
            # Set minimum TLS version to 1.2 (MongoDB Atlas requirement)
            ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
            # Allow legacy server connect (fixes OpenSSL 3.5+ compatibility issues)
            ssl_context.options |= 0x4  # OP_LEGACY_SERVER_CONNECT

            config.mongodb_client = AsyncIOMotorClient(
                config.settings.MONGODB_URI,
                tlsCAFile=None,  # Use system CA certificates
                ssl_context=ssl_context
            )
            # Verify connection
            await config.mongodb_client.admin.command('ping')
            print("[OK] MongoDB connected successfully")
        except Exception as e:
            print(f"[WARNING] MongoDB connection failed: {e}")
            print("  RAG features will be unavailable")
            config.mongodb_client = None
    else:
        print("[WARNING] MONGODB_URI not configured")
        print("  RAG features will be unavailable")

    yield

    # Shutdown: Close MongoDB connection
    if config.mongodb_client:
        config.mongodb_client.close()
        print("[OK] MongoDB connection closed")

app = FastAPI(lifespan=lifespan)

@app.get("/")
@app.head("/")
def health_check():
    """
    Health check endpoint for monitoring and CI/CD.
    Supports both GET and HEAD methods for wait-on compatibility.
    """
    return {"status": "ok", "service": "backend"}

@app.get("/health")
@app.head("/health")
def kubernetes_health():
    """
    Dedicated health check endpoint for Kubernetes probes.
    Returns minimal response to reduce log noise.
    """
    return {"status": "healthy"}

# Include routers
app.include_router(chat.api_router)
app.include_router(documents.router)
