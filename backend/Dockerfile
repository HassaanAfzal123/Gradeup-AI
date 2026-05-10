# Backend Dockerfile for Gradeup AI
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# PyPI can flake on flaky Wi‑Fi; retry longer (still fails if DNS is totally down)
ENV PIP_DEFAULT_TIMEOUT=120 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install --no-cache-dir --retries 15 -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Health check: first boot loads embedding model; /health only after uvicorn is up
HEALTHCHECK --interval=30s --timeout=15s --start-period=1800s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
