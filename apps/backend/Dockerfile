# Backend Dockerfile for FastAPI (development)
# Use Debian Bullseye base image to avoid OpenSSL 3.5 compatibility issues
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies for SSL/TLS and MongoDB
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Install pip and setuptools
RUN pip install --upgrade pip setuptools

# Copy pyproject.toml and install dependencies
COPY pyproject.toml ./
RUN pip install .

# Copy the rest of the source code
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Start FastAPI app with reload for development
CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
