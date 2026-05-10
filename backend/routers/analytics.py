"""
Analytics router - Mastery tracking, recommendations, and progress
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel

from database.connection import get_db
from database.models import User, Weakness, Quiz as QuizModel, PDF as PDFModel
from auth.middleware import get_current_user
from services.learner_profile_service import learner_profile_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ------------------------------------------------------------------
# Pydantic models
# ------------------------------------------------------------------
class WeaknessResponse(BaseModel):
    concept: str
    frequency: int
    last_incorrect: str


class MasteryItemResponse(BaseModel):
    concept: str
    mastery_score: float
    correct: int
    incorrect: int
    last_seen: str | None = None


class ProgressResponse(BaseModel):
    total_quizzes: int
    average_score: float
    total_pdfs: int
    weak_concepts_count: int
    mastered_concepts_count: int


class RecommendationResponse(BaseModel):
    priority_review: List[str]
    strong_concepts: List[str]
    suggestion: str


# ------------------------------------------------------------------
# Endpoints
# ------------------------------------------------------------------
@router.get("/weaknesses", response_model=List[WeaknessResponse])
async def get_weaknesses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    weaknesses = (
        db.query(Weakness)
        .filter(Weakness.user_id == current_user.id)
        .order_by(Weakness.frequency.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "concept": w.concept,
            "frequency": w.frequency,
            "last_incorrect": w.last_incorrect_at.isoformat(),
        }
        for w in weaknesses
    ]


@router.get("/mastery", response_model=List[MasteryItemResponse])
async def get_mastery_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Full concept-mastery profile for the current user."""
    return learner_profile_service.get_full_profile(db, str(current_user.id))


@router.get("/recommendations", response_model=RecommendationResponse)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Personalized study recommendations derived from the mastery model."""
    return learner_profile_service.get_recommendations(db, str(current_user.id))


@router.get("/progress", response_model=ProgressResponse)
async def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    total_quizzes = (
        db.query(QuizModel).filter(QuizModel.user_id == current_user.id).count()
    )
    avg_score = (
        db.query(func.avg(QuizModel.score))
        .filter(QuizModel.user_id == current_user.id)
        .scalar()
        or 0.0
    )
    total_pdfs = (
        db.query(PDFModel).filter(PDFModel.user_id == current_user.id).count()
    )
    weak_concepts_count = (
        db.query(Weakness).filter(Weakness.user_id == current_user.id).count()
    )

    from database.models import ConceptMastery
    mastered_concepts_count = (
        db.query(ConceptMastery)
        .filter(
            ConceptMastery.user_id == current_user.id,
            ConceptMastery.mastery_score >= 0.8,
        )
        .count()
    )

    return {
        "total_quizzes": total_quizzes,
        "average_score": float(avg_score),
        "total_pdfs": total_pdfs,
        "weak_concepts_count": weak_concepts_count,
        "mastered_concepts_count": mastered_concepts_count,
    }
