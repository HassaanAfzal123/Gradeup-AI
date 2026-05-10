"""
Quiz router - Generate, submit, and track quizzes with adaptive weakness targeting
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from logging_config import get_logger

from database.connection import get_db
from database.models import User, PDF as PDFModel, Quiz as QuizModel, Weakness
from auth.middleware import get_current_user
from services.rag_service import rag_service
from services.langchain_service import langchain_service
from services.groq_client import groq_client
from services.learner_profile_service import learner_profile_service

router = APIRouter(prefix="/quiz", tags=["Quiz"])
logger = get_logger(__name__)


# Pydantic models
class QuizGenerateRequest(BaseModel):
    pdf_id: str
    topic: str = ""
    num_questions: int = 5
    difficulty: str = "medium"
    adaptive: bool = False
    model_name: str | None = None  # override default model for comparison experiments
    temperature: float = 0.7


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    user_answers: dict


class QuizResponse(BaseModel):
    quiz_id: str
    questions: List[dict]
    topic: str
    adaptive: bool = False


class QuizResultResponse(BaseModel):
    quiz_id: str
    score: float
    correct_answers: int
    total_questions: int
    weak_concepts: List[str]
    mastery_updates: List[dict] = []


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate quiz from PDF — optionally in adaptive mode that targets weak concepts."""
    logger.info("Quiz generation requested", extra={
        "user_id": str(current_user.id),
        "pdf_id": request.pdf_id,
        "difficulty": request.difficulty,
        "adaptive": request.adaptive,
    })

    pdf = db.query(PDFModel).filter(
        PDFModel.id == request.pdf_id,
        PDFModel.user_id == current_user.id
    ).first()

    if not pdf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found")

    quiz_topic = request.topic.strip() if request.topic.strip() else f"content from {pdf.filename}"

    # Fetch weak concepts when adaptive mode is on
    weak_concepts: list[str] = []
    if request.adaptive:
        profile_weak = learner_profile_service.get_weak_concepts(db, str(current_user.id))
        weak_concepts = [w["concept"] for w in profile_weak]
        logger.info(f"Adaptive mode: targeting {len(weak_concepts)} weak concepts")

    context = await rag_service.get_document_context(
        user_id=str(current_user.id),
        file_id=pdf.file_id,
        topic=quiz_topic if request.topic.strip() else "",
        top_k=30,
    )

    from config import settings as app_settings
    effective_model = request.model_name or app_settings.GROQ_MODEL

    try:
        questions = await langchain_service.generate_quiz_with_agent(
            context=context,
            topic=quiz_topic,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            weak_concepts=weak_concepts,
            adaptive_mode=request.adaptive,
            model_name=effective_model,
            temperature=request.temperature,
        )
    except Exception as e:
        error_msg = str(e)
        if "decommissioned" in error_msg.lower():
            detail = f"Model '{effective_model}' has been decommissioned by Groq. Choose another model."
        else:
            detail = f"Quiz generation failed: {error_msg[:200]}"
        logger.error(f"Quiz generation exception: {error_msg}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz questions — LLM returned unparseable output",
        )

    quiz = QuizModel(
        user_id=current_user.id,
        pdf_id=pdf.id,
        topic=quiz_topic,
        questions=questions,
        user_answers={},
        total_questions=len(questions),
        model_used=effective_model,
        is_adaptive=1 if request.adaptive else 0,
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return {
        "quiz_id": str(quiz.id),
        "questions": questions,
        "topic": quiz_topic,
        "adaptive": request.adaptive,
    }


@router.post("/submit", response_model=QuizResultResponse)
async def submit_quiz(
    request: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit quiz answers, update mastery profile, and return results."""
    quiz = db.query(QuizModel).filter(
        QuizModel.id == request.quiz_id,
        QuizModel.user_id == current_user.id,
    ).first()

    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")

    # Grade
    correct_count = 0
    incorrect_answers = []

    for question in quiz.questions:
        q_id = str(question["id"])
        correct_answer = question["correct_answer"]
        user_answer = request.user_answers.get(q_id, "")

        if user_answer.strip() == correct_answer.strip():
            correct_count += 1
        else:
            incorrect_answers.append({
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "concept": question.get("concept", quiz.topic),
            })

    score = (correct_count / quiz.total_questions) * 100 if quiz.total_questions > 0 else 0

    quiz.user_answers = request.user_answers
    quiz.score = score
    quiz.correct_answers = correct_count

    # --- Update ConceptMastery via learner profile service ---
    mastery_updates = learner_profile_service.update_mastery_from_quiz(
        db=db,
        user_id=str(current_user.id),
        questions=quiz.questions,
        user_answers=request.user_answers,
        pdf_id=str(quiz.pdf_id),
    )

    # Legacy weakness tracking (kept for backward compatibility)
    weak_concepts = []
    if incorrect_answers:
        concept_tags = [a.get("concept", "") for a in incorrect_answers if a.get("concept")]
        groq_concepts = await groq_client.analyze_weaknesses(incorrect_answers)
        weak_concepts = list(set(concept_tags + groq_concepts))

        for concept in weak_concepts:
            weakness = db.query(Weakness).filter(
                Weakness.user_id == current_user.id,
                Weakness.concept == concept,
            ).first()
            if weakness:
                weakness.frequency += 1
            else:
                db.add(Weakness(user_id=current_user.id, concept=concept, frequency=1))

    db.commit()

    return {
        "quiz_id": str(quiz.id),
        "score": score,
        "correct_answers": correct_count,
        "total_questions": quiz.total_questions,
        "weak_concepts": weak_concepts,
        "mastery_updates": mastery_updates,
    }


@router.get("/history")
async def get_quiz_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all quizzes for current user"""
    quizzes = db.query(QuizModel).filter(
        QuizModel.user_id == current_user.id
    ).order_by(QuizModel.completed_at.desc()).all()
    
    return [
        {
            "id": str(quiz.id),
            "topic": quiz.topic,
            "score": quiz.score,
            "completed_at": quiz.completed_at.isoformat()
        }
        for quiz in quizzes
    ]
