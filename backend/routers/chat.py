"""
Chat router - Weakness-aware RAG Q&A system
"""
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from logging_config import get_logger

from database.connection import get_db
from database.models import User, PDF as PDFModel, Chat as ChatModel
from auth.middleware import get_current_user
from services.rag_service import rag_service
from services.groq_client import groq_client
from services.learner_profile_service import learner_profile_service

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = get_logger(__name__)


# Pydantic models
class ChatRequest(BaseModel):
    pdf_id: str
    question: str
    adaptive: bool = False
    model_name: str | None = None  # override for model comparison experiments


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    chat_id: str
    adaptive: bool = False
    model_used: str | None = None
    latency_ms: int | None = None


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask a question about a PDF using RAG with optional adaptive tutoring."""
    logger.info("Chat question received", extra={
        "user_id": str(current_user.id),
        "pdf_id": request.pdf_id,
        "adaptive": request.adaptive,
    })

    pdf = db.query(PDFModel).filter(
        PDFModel.id == request.pdf_id,
        PDFModel.user_id == current_user.id,
    ).first()

    if not pdf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found")

    retrieval_result = await rag_service.query_document(
        user_id=str(current_user.id),
        file_id=pdf.file_id,
        query=request.question,
        top_k=8,
    )

    chunks = retrieval_result.get("chunks", [])
    chunk_texts = [chunk["text"] for chunk in chunks]

    # Build optional weakness context for the LLM
    weakness_hint = ""
    if request.adaptive:
        weakness_hint = learner_profile_service.weakness_summary_for_prompt(
            db, str(current_user.id)
        )

    from services.comprehensive_answer import answer_question_comprehensive
    from config import settings as app_settings

    effective_model = request.model_name or app_settings.GROQ_MODEL

    groq_result = await answer_question_comprehensive(
        client=groq_client.client,
        model=effective_model,
        question=request.question,
        context_chunks=chunk_texts,
        weakness_context=weakness_hint,
    )

    raw_answer = groq_result.get("answer", "Sorry, I couldn't generate an answer.")
    answer = re.sub(r"\[(?:Chunk|CHUNK)\s*\d+(?:\s*,\s*(?:Chunk|CHUNK)\s*\d+)*\]", "", raw_answer)
    answer = re.sub(r"  +", " ", answer).strip()

    logger.info("Answer generated", extra={
        "answer_length": len(answer),
        "num_sources": len(chunks),
        "adaptive": request.adaptive,
    })

    chat = db.query(ChatModel).filter(
        ChatModel.user_id == current_user.id,
        ChatModel.pdf_id == pdf.id,
    ).first()

    if not chat:
        chat = ChatModel(user_id=current_user.id, pdf_id=pdf.id, messages=[])
        db.add(chat)

    timestamp = datetime.utcnow().isoformat()
    chat.messages.append({"role": "user", "content": request.question, "timestamp": timestamp})
    chat.messages.append({"role": "assistant", "content": answer, "timestamp": timestamp})

    db.commit()
    db.refresh(chat)

    return {
        "answer": answer,
        "sources": chunks,
        "chat_id": str(chat.id),
        "adaptive": request.adaptive,
        "model_used": groq_result.get("model_used", effective_model),
        "latency_ms": groq_result.get("latency_ms"),
    }


@router.get("/history/{pdf_id}", response_model=List[ChatMessage])
async def get_chat_history(
    pdf_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a PDF"""
    chat = db.query(ChatModel).filter(
        ChatModel.pdf_id == pdf_id,
        ChatModel.user_id == current_user.id
    ).first()
    
    if not chat:
        return []
    
    return chat.messages


@router.delete("/{chat_id}")
async def clear_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear chat history"""
    chat = db.query(ChatModel).filter(
        ChatModel.id == chat_id,
        ChatModel.user_id == current_user.id
    ).first()
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )
    
    db.delete(chat)
    db.commit()
    
    return {"message": "Chat history cleared"}
