# syntax=docker/dockerfile:1
# Backend Dockerfile for Gradeup AI
# If build fails with "Name or service not known" → Docker cannot resolve DNS (see README / fix Docker DNS below).

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Pip cache: speeds rebuilds after one successful download (needs BuildKit — default in Docker Desktop).
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

RUN mkdir -p uploads

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=15s --start-period=180s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
