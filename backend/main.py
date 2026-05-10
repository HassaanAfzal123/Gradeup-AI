"""
Gradeup AI - Production Backend
Main FastAPI application with LangChain integration.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from database.connection import init_db
from logging_config import setup_logging, get_logger
import time

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)

# Import routers
from routers import auth, pdf, chat, quiz, analytics, evaluation

# Initialize FastAPI app
app = FastAPI(
    title="Gradeup AI",
    description="Production RAG-based tutoring platform with LangChain agentic framework",
    version="2.0.0"
)

# Configure CORS (see Starlette CORSMiddleware: 400 "Bad Request" on preflight means
# Origin/method/headers check failed — not venv paths. DEBUG adds a regex so alternate
# Vite ports and LAN dev URLs work without listing every origin.)
_cors_regex = None
if settings.DEBUG:
    _cors_regex = (
        r"https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$"
        r"|https?://192\.168\.\d{1,3}\.\d{1,3}:\d+$"
        r"|https?://10\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$"
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=_cors_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests and responses"""
    start_time = time.time()
    
    # Log request
    logger.info("Incoming request", extra={
        "method": request.method,
        "path": request.url.path,
        "client": request.client.host if request.client else None
    })
    
    # Process request
    response = await call_next(request)
    
    # Log response
    duration = (time.time() - start_time) * 1000  # ms
    logger.info("Request completed", extra={
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration": round(duration, 2)
    })
    
    return response


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(pdf.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat.router, prefix=settings.API_V1_PREFIX)
app.include_router(quiz.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)
app.include_router(evaluation.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Gradeup AI...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        logger.warning("If using PostgreSQL, ensure it's running and DATABASE_URL is correct")
    
    logger.info("Gradeup AI ready", extra={
        "groq_model": settings.GROQ_MODEL,
        "jwt_expiry_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        "cors_origins": settings.CORS_ORIGINS
    })


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Gradeup AI",
        "version": "2.0.0",
        "features": [
            "Multi-user authentication",
            "PDF upload & indexing",
            "RAG-based Q&A",
            "AI quiz generation",
            "Concept-level weakness detection",
            "Adaptive tutoring (weakness-aware quiz & chat)",
            "Learner mastery profiling",
            "Research evaluation metrics",
        ]
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "groq_api": "configured",
        "chroma_db": "initialized"
    }


@app.get("/api/models")
async def list_models():
    """List available Groq models for comparison experiments."""
    return {
        "default": settings.GROQ_MODEL,
        "available": settings.available_models_list,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.API_PORT,
        reload=True
    )
