# Backend (FastAPI) – Nx Monorepo Example

This is the backend application for the Nx monorepo, built with [FastAPI](https://fastapi.tiangolo.com/) and Python. It provides a RESTful API that integrates with the Next.js frontend and follows modern Python development best practices.

---

## Features

- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.10+** with type hints and modern syntax
- **RAG (Retrieval-Augmented Generation)** - Document upload, vector search, and AI-powered chat
- **MongoDB Atlas Vector Search** - Scalable vector database for embeddings
- **OpenAI Integration** - GPT-3.5 Turbo for chat and embeddings
- **Comprehensive Testing** with pytest + pytest-asyncio + httpx
- **Dependency Management** via pyproject.toml (PEP 621)
- **Docker Support** with optimized containerization
- **Kubernetes Ready** with Helm charts and secure secret management
- **Nx Integration** for monorepo management
- **API Convention** - All endpoints prefixed with `/api`


---

## Project Structure

```
apps/backend/
├── main.py              # FastAPI application entry point
├── config.py            # Environment configuration and settings
├── pyproject.toml       # Python dependencies and build config
├── project.json         # Nx targets for build/serve/test
├── pytest.ini          # pytest configuration
├── routers/            # API route handlers
│   ├── chat.py         # Chat and RAG endpoints
│   └── documents.py    # Document management endpoints
├── services/           # Business logic layer
│   ├── rag_service.py      # RAG query processing
│   ├── document_service.py # Document upload & processing
│   └── vector_store.py     # MongoDB vector operations
├── models/             # Pydantic data models
│   ├── chat.py         # Chat request/response models
│   └── document.py     # Document models
├── utils/              # Utility functions
│   └── file_parser.py  # File parsing (PDF, DOCX, etc.)
├── tests/              # Test suite
│   ├── __init__.py
│   └── test_main.py
├── helm/               # Kubernetes Helm charts
│   ├── templates/
│   ├── values.yaml
│   ├── secrets.example.yaml    # Secret template (sensitive info redacted)
│   ├── QUICK_START.md         # Quick deployment guide
│   └── K8S_SECRETS_GUIDE.md   # Complete Secrets management documentation
├── Dockerfile          # Container configuration
├── .dockerignore       # Docker ignore patterns
├── .env.example        # Environment variables template (sensitive info redacted)
└── README.md           # This file
```

---

## Development

### 1. Install dependencies

From the monorepo root:
```sh
npx nx build backend
```

This will install all Python dependencies including:
- FastAPI & Uvicorn
- OpenAI SDK
- LangChain & MongoDB integrations
- File parsers (PyPDF2, python-docx, openpyxl, etc.)

### 2. Configure environment variables

Create a `.env` file in `apps/backend/`:
```bash
# Copy the example file
cp apps/backend/.env.example apps/backend/.env

# Edit .env and fill in your API keys
# Note: .env is in .gitignore and will NOT be committed
```

Required environment variables:
```bash
# OpenAI API Key (required for chat and embeddings)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# MongoDB Atlas Connection (required for RAG features)
MONGODB_URI=mongodb+srv://username:********@cluster.mongodb.net/?retryWrites=true&w=majority

# Admin API Key (required for document management)
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
ADMIN_API_KEY=********************************
```

**Note**: Sensitive information is redacted with `*`. Please fill in actual API keys when using.

### 3. Start the backend

From the monorepo root:
```sh
npx nx serve backend
```

The API will be available at [http://localhost:8000](http://localhost:8000).

You should see:
```
[OK] MongoDB connected successfully
INFO:     Application startup complete.
```

If MongoDB is not configured, you'll see:
```
[WARNING] MONGODB_URI not configured
  RAG features will be unavailable
```

### 4. API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Testing

### Test Commands

```bash
# Run tests via Nx (recommended)
nx test backend

# Run tests directly
cd apps/backend
python -m pytest

# Run tests with verbose output
python -m pytest -v
```

### Test Configuration

- **pytest** - Core testing framework
- **pytest-asyncio** - Async test support
- **httpx** - HTTP client for testing FastAPI endpoints
- **pytest.ini** - Test discovery and default options

### Test Structure

- **Test Files**: Located in `tests/` directory
- **Test Discovery**: Automatically finds `test_*.py` files
- **Naming Convention**: `test_<module_name>.py`
- **Test Classes**: `Test<ClassName>` for organization

---

## API Endpoints

### Health Check

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/` | Health check | `{"status": "ok", "service": "backend"}` |
| GET | `/ping` | Ping endpoint | `{"result": "pong"}` |

### Chat Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/chat` | Send message to AI chatbot (with RAG support) | No |

**Request Body:**
```json
{
  "message": "What is Draco's experience?",
  "history": [],
  "use_rag": true
}
```

**Response:**
```json
{
  "response": "Draco has 12+ years of experience...",
  "sources": [
    {
      "document_id": "abc123",
      "filename": "resume.pdf",
      "content": "Draco Cheng is a Senior Software Engineer...",
      "score": 0.95
    }
  ]
}
```

### Document Management Endpoints (Admin Only)

All document endpoints require `X-API-Key` header with admin API key.

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/documents` | List all uploaded documents | No |
| POST | `/api/documents/upload` | Upload document (PDF, DOCX, XLSX, MD, TXT) | **Yes** |
| DELETE | `/api/documents/{id}` | Delete document and all its chunks | **Yes** |
| GET | `/api/documents/{id}` | Get document metadata | No |
| GET | `/api/documents/stats/storage` | Get storage statistics | No |

**Upload Example:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "X-API-Key: your-admin-key-here" \
  -F "file=@resume.pdf"
```

**Response:**
```json
{
  "id": "abc123-def456",
  "filename": "resume.pdf",
  "status": "success",
  "chunk_count": 15,
  "message": "Document processed into 15 chunks"
}
```

---

## Configuration

### Environment Variables

#### Required (for RAG features)

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for chat and embeddings | `sk-xxxxxxxxxxxxxxxx` |
| `MONGODB_URI` | MongoDB Atlas connection string | `mongodb+srv://user:****@cluster.mongodb.net/` |
| `ADMIN_API_KEY` | Admin key for document management | Generate with `secrets.token_urlsafe(32)` |

#### Optional (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_DB_NAME` | `personal_website` | MongoDB database name |
| `MONGODB_COLLECTION` | `documents` | MongoDB collection name |
| `VECTOR_INDEX_NAME` | `vector_index` | Vector search index name |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `CHUNK_SIZE` | `1000` | Text chunk size for splitting |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `MAX_FILE_SIZE_MB` | `10` | Maximum upload file size |

### Dependencies

Core dependencies are managed in `pyproject.toml`:

**Web Framework:**
- **fastapi**: Web framework
- **uvicorn**: ASGI server

**AI & RAG:**
- **openai**: OpenAI API client
- **langchain**: LLM framework
- **langchain-openai**: OpenAI integration
- **langchain-mongodb**: MongoDB vector store
- **langchain-text-splitters**: Text chunking

**Database:**
- **motor**: Async MongoDB driver
- **pymongo**: MongoDB driver with SRV support

**File Processing:**
- **PyPDF2**: PDF parsing
- **pdfplumber**: Advanced PDF parsing
- **python-docx**: Word document parsing
- **openpyxl**: Excel file parsing
- **python-multipart**: File upload support

**Testing:**
- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **httpx**: HTTP client for testing

---

## Docker

### Build and Run

```bash
# Build the image
docker build -t backend .

# Run the container
docker run -p 8000:8000 backend

# Or use docker-compose from root
docker-compose up backend
```

### Dockerfile Features

- Multi-stage build for optimization
- Python 3.10+ base image
- Production-ready configuration
- Health check endpoint support

---

## Kubernetes Deployment

### Quick Start

The fastest way to deploy to Kubernetes:

```bash
# 1. Create Kubernetes Secret with your API keys
kubectl create secret generic backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-your-key-here' \
  --from-literal=MONGODB_URI='mongodb+srv://user:****@cluster.mongodb.net/' \
  --from-literal=ADMIN_API_KEY='your-generated-key'

# 2. Deploy with Helm
cd apps/backend/helm
helm upgrade --install backend . \
  --set image.repository=your-registry/backend \
  --set image.tag=latest

# 3. Verify deployment
kubectl get pods -l app=backend
kubectl logs -l app=backend --tail=20
```

### Secret Management

Sensitive information (API keys, connection strings) is managed via **Kubernetes Secrets**:

#### Method 1: Using kubectl (Recommended for Production)

```bash
# Create all secrets with one command
kubectl create secret generic backend-secrets \
  --from-literal=OPENAI_API_KEY='sk-****' \
  --from-literal=MONGODB_URI='mongodb+srv://****' \
  --from-literal=ADMIN_API_KEY='****'
```

#### Method 2: Using YAML File (Development/Testing)

```bash
# 1. Copy the example file
cp apps/backend/helm/secrets.example.yaml apps/backend/helm/secrets.yaml

# 2. Edit secrets.yaml and fill in real API keys
# Note: secrets.yaml is in .gitignore and will not be committed to Git

# 3. Deploy the Secret
kubectl apply -f apps/backend/helm/secrets.yaml

# 4. Deploy the application
helm upgrade --install backend apps/backend/helm
```

#### Generate Admin API Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Helm Configuration

Configuration in `helm/values.yaml`:

```yaml
# Kubernetes Secret configuration
secrets:
  enabled: true              # Enable Secret injection
  name: backend-secrets      # Secret name

# Non-sensitive environment variables (can be public)
env:
  MONGODB_DB_NAME: "personal_website"
  MONGODB_COLLECTION: "documents"
  VECTOR_INDEX_NAME: "vector_index"
  EMBEDDING_MODEL: "text-embedding-3-small"
  CHUNK_SIZE: "1000"
  CHUNK_OVERLAP: "200"
  MAX_FILE_SIZE_MB: "10"

# Resource limits
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

### Verify Deployment

```bash
# Check Pod status
kubectl get pods -l app=backend

# Check logs (should see MongoDB connection success)
kubectl logs -l app=backend --tail=20
# Expected output:
# [OK] MongoDB connected successfully
# INFO:     Application startup complete.

# Check if Secret exists
kubectl get secret backend-secrets

# Port-forward for testing
kubectl port-forward service/backend 8000:8000
curl http://localhost:8000/
```

### Update Secrets

```bash
# Delete old Secret
kubectl delete secret backend-secrets

# Create new Secret
kubectl create secret generic backend-secrets \
  --from-literal=OPENAI_API_KEY='new-key' \
  --from-literal=MONGODB_URI='new-uri' \
  --from-literal=ADMIN_API_KEY='new-admin-key'

# Restart deployment (to load new Secret)
kubectl rollout restart deployment backend
```

### Detailed Documentation

More deployment options and security best practices:
- **[helm/QUICK_START.md](helm/QUICK_START.md)** - Quick deployment guide
- **[helm/K8S_SECRETS_GUIDE.md](helm/K8S_SECRETS_GUIDE.md)** - Complete Secrets management documentation
- **[helm/secrets.example.yaml](helm/secrets.example.yaml)** - Secret YAML example

---

## Nx Integration

### Available Targets

- **`nx build backend`** - Install Python dependencies
- **`nx serve backend`** - Start development server
- **`nx test backend`** - Run pytest tests

### Cross-Platform Commands

All commands are now cross-platform compatible through Nx:
- **`nx build backend`** - Install dependencies
- **`nx serve backend`** - Start development server
- **`nx test backend`** - Run tests

---

## Best Practices

### Code Quality

- Use Python type hints for all functions
- Follow PEP 8 style guidelines
- Write comprehensive docstrings
- Keep functions small and focused

### Testing

- Test both success and error cases
- Use descriptive test names
- Mock external dependencies
- Maintain high test coverage

### API Design

- Use consistent endpoint naming
- Implement proper error handling
- Return structured JSON responses
- Follow RESTful conventions

### Security

- **Never commit secrets** - Use `.env` locally and Kubernetes Secrets in production
- **Rotate API keys regularly** - Update secrets every 3-6 months
- **Use HTTPS in production** - Encrypt all traffic
- **Validate file uploads** - Check file type, size, and content
- **Limit API access** - Use API keys for admin operations
- **Monitor logs** - Track API usage and errors

---

## Security Notes

### Sensitive Information Protection

All sensitive information (API keys, passwords, connection strings) in this project has been redacted or removed:

✅ **Protected files:**
- `.env` - Local environment variables (in `.gitignore`)
- `helm/secrets.yaml` - Kubernetes Secrets (in `.gitignore`)
- All examples in documentation use `****` or `xxxx` to redact real values

✅ **Example files (safe to commit):**
- `.env.example` - Environment variables template
- `helm/secrets.example.yaml` - Kubernetes Secret template
- All example code in documentation

⚠️ **Important reminders:**
- Never commit real API keys to Git
- Regularly check Git history for sensitive information
- Use `git-secrets` or `truffleHog` tools for scanning
- If leaks are discovered, immediately regenerate and replace keys

### Best Practices

1. **Local development:** Use `.env` file
2. **Kubernetes deployment:** Use Kubernetes Secrets
3. **CI/CD:** Use environment variables or Secret Manager
4. **Generate strong passwords:** `python -c "import secrets; print(secrets.token_urlsafe(32))"`

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [PEP 621 - pyproject.toml](https://peps.python.org/pep-0621/)
- [Nx Documentation](https://nx.dev)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [LangChain Documentation](https://python.langchain.com/)