"""
Evaluation router — comprehensive endpoints for research paper analysis:
- Baseline vs Adaptive comparison
- Per-model comparison metrics
- Data/document statistics (chunk distribution, coverage)
- Ablation study runner (varying chunk_size, top_k, temperature)
"""
import time
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database.connection import get_db
from database.models import User, Quiz as QuizModel, PDF as PDFModel, ConceptMastery
from auth.middleware import get_current_user
from config import settings
from logging_config import get_logger

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])
logger = get_logger(__name__)


# ── Response models ──────────────────────────────────────────────────

class ScoreBucket(BaseModel):
    quiz_id: str
    score: float
    total_questions: int
    topic: str
    model_used: str | None = None
    is_adaptive: bool = False


class EvaluationSummary(BaseModel):
    total_quizzes: int
    baseline_avg_score: float
    adaptive_avg_score: float
    baseline_count: int
    adaptive_count: int
    mastery_coverage: int
    weak_concept_count: int
    improvement_delta: float


class ModelComparisonRow(BaseModel):
    model: str
    quiz_count: int
    avg_score: float
    min_score: float
    max_score: float


class DocumentStats(BaseModel):
    pdf_id: str
    filename: str
    total_chunks: int
    file_size_kb: float
    avg_chunk_length: float | None = None
    chunk_lengths: List[int] = []


class AblationRequest(BaseModel):
    pdf_id: str
    topic: str = ""
    num_questions: int = 5
    models: List[str] = []
    temperatures: List[float] = [0.3, 0.5, 0.7, 0.9]
    difficulties: List[str] = ["easy", "medium", "hard"]


class AblationResultRow(BaseModel):
    model: str
    temperature: float
    difficulty: str
    questions_generated: int
    avg_options: float
    has_explanations: bool
    generation_time_ms: int


class ComponentAblationRequest(BaseModel):
    pdf_id: str
    topic: str = ""
    num_questions: int = 5
    model: str = ""
    temperature: float = 0.3
    difficulty: str = "medium"


class ComponentAblationRow(BaseModel):
    configuration: str
    avg_score: float
    questions_generated: int
    generation_time_ms: int
    description: str


# ── Endpoints ────────────────────────────────────────────────────────

@router.get("/summary", response_model=EvaluationSummary)
async def evaluation_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compare baseline vs adaptive quiz scores for the current user."""
    quizzes = (
        db.query(QuizModel)
        .filter(QuizModel.user_id == current_user.id, QuizModel.score.isnot(None))
        .all()
    )

    baseline_scores: list[float] = []
    adaptive_scores: list[float] = []

    for q in quizzes:
        is_adaptive = bool(q.is_adaptive) or any(
            question.get("targeted", False) for question in (q.questions or [])
        )
        (adaptive_scores if is_adaptive else baseline_scores).append(q.score)

    baseline_avg = sum(baseline_scores) / len(baseline_scores) if baseline_scores else 0.0
    adaptive_avg = sum(adaptive_scores) / len(adaptive_scores) if adaptive_scores else 0.0

    mastery_coverage = (
        db.query(ConceptMastery).filter(ConceptMastery.user_id == current_user.id).count()
    )
    weak_count = (
        db.query(ConceptMastery)
        .filter(ConceptMastery.user_id == current_user.id, ConceptMastery.mastery_score < 0.4)
        .count()
    )

    return {
        "total_quizzes": len(quizzes),
        "baseline_avg_score": round(baseline_avg, 2),
        "adaptive_avg_score": round(adaptive_avg, 2),
        "baseline_count": len(baseline_scores),
        "adaptive_count": len(adaptive_scores),
        "mastery_coverage": mastery_coverage,
        "weak_concept_count": weak_count,
        "improvement_delta": round(adaptive_avg - baseline_avg, 2),
    }


@router.get("/quiz-scores", response_model=List[ScoreBucket])
async def quiz_score_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return per-quiz scores in chronological order for charting."""
    quizzes = (
        db.query(QuizModel)
        .filter(QuizModel.user_id == current_user.id, QuizModel.score.isnot(None))
        .order_by(QuizModel.completed_at.asc())
        .all()
    )
    return [
        {
            "quiz_id": str(q.id),
            "score": q.score,
            "total_questions": q.total_questions,
            "topic": q.topic or "",
            "model_used": q.model_used,
            "is_adaptive": bool(q.is_adaptive),
        }
        for q in quizzes
    ]


@router.get("/model-comparison", response_model=List[ModelComparisonRow])
async def model_comparison(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Aggregate quiz scores grouped by model_used."""
    quizzes = (
        db.query(QuizModel)
        .filter(QuizModel.user_id == current_user.id, QuizModel.score.isnot(None))
        .all()
    )

    by_model: dict[str, list[float]] = {}
    for q in quizzes:
        model = q.model_used or settings.GROQ_MODEL
        by_model.setdefault(model, []).append(q.score)

    return [
        {
            "model": model,
            "quiz_count": len(scores),
            "avg_score": round(sum(scores) / len(scores), 2),
            "min_score": round(min(scores), 2),
            "max_score": round(max(scores), 2),
        }
        for model, scores in by_model.items()
    ]


@router.get("/document-stats", response_model=List[DocumentStats])
async def document_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return chunk distribution and document statistics for all user PDFs."""
    from services.rag_service import rag_service

    pdfs = db.query(PDFModel).filter(PDFModel.user_id == current_user.id).all()
    results = []

    for p in pdfs:
        collection = rag_service._get_user_collection(str(current_user.id))
        try:
            data = collection.get(where={"file_id": p.file_id}, include=["documents"])
            docs = data.get("documents", [])
            lengths = [len(d.split()) for d in docs] if docs else []
        except Exception:
            lengths = []

        results.append({
            "pdf_id": str(p.id),
            "filename": p.filename,
            "total_chunks": p.total_chunks or len(lengths),
            "file_size_kb": round((p.file_size or 0) / 1024, 2),
            "avg_chunk_length": round(sum(lengths) / len(lengths), 1) if lengths else None,
            "chunk_lengths": lengths,
        })

    return results


@router.post("/ablation", response_model=List[AblationResultRow])
async def run_ablation(
    request: AblationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Run an ablation study: generate quizzes across different models,
    temperatures, and difficulties, then report quality metrics.
    """
    pdf = db.query(PDFModel).filter(
        PDFModel.id == request.pdf_id, PDFModel.user_id == current_user.id
    ).first()
    if not pdf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found")

    from services.rag_service import rag_service
    from services.langchain_service import langchain_service

    context = await rag_service.get_document_context(
        user_id=str(current_user.id),
        file_id=pdf.file_id,
        topic=request.topic or None,
        top_k=20,
    )

    models = request.models or settings.available_models_list
    results: list[dict] = []

    for model in models:
        for temp in request.temperatures:
            for diff in request.difficulties:
                t0 = time.time()
                try:
                    questions = await langchain_service.generate_quiz_with_agent(
                        context=context,
                        topic=request.topic or f"content from {pdf.filename}",
                        num_questions=request.num_questions,
                        difficulty=diff,
                        model_name=model,
                        temperature=temp,
                    )
                except Exception as e:
                    logger.warning(f"Ablation failed for {model}/{temp}/{diff}: {e}")
                    questions = []

                elapsed = round((time.time() - t0) * 1000)

                avg_opts = 0.0
                has_expl = False
                if questions:
                    opts_counts = [len(q.get("options", [])) for q in questions]
                    avg_opts = round(sum(opts_counts) / len(opts_counts), 1) if opts_counts else 0
                    has_expl = all(bool(q.get("explanation")) for q in questions)

                results.append({
                    "model": model,
                    "temperature": temp,
                    "difficulty": diff,
                    "questions_generated": len(questions),
                    "avg_options": avg_opts,
                    "has_explanations": has_expl,
                    "generation_time_ms": elapsed,
                })

                # Small delay to respect rate limits
                await asyncio.sleep(2)

    return results


@router.post("/component-ablation", response_model=List[ComponentAblationRow])
async def component_ablation(
    request: ComponentAblationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Component ablation study: generate quizzes with different system components
    enabled or disabled to measure the contribution of each component.

    Tests the following configurations:
    1. Full System (all components enabled)
    2. No Weakness Tracking (adaptive without weak concept injection)
    3. No Adaptive Mode (pure baseline quiz generation)
    4. No RAG (random questions without document context)
    5. No Concept Mastery (no mastery profile influence)
    """
    pdf = db.query(PDFModel).filter(
        PDFModel.id == request.pdf_id, PDFModel.user_id == current_user.id
    ).first()
    if not pdf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF not found")

    from services.rag_service import rag_service
    from services.langchain_service import langchain_service

    model = request.model or settings.GROQ_MODEL

    # Get full RAG context
    full_context = await rag_service.get_document_context(
        user_id=str(current_user.id),
        file_id=pdf.file_id,
        topic=request.topic or None,
        top_k=10,
    )

    # Get user's weak concepts
    weak_concepts = []
    mastery_rows = (
        db.query(ConceptMastery)
        .filter(
            ConceptMastery.user_id == current_user.id,
            ConceptMastery.mastery_score < 0.7,
        )
        .order_by(ConceptMastery.mastery_score.asc())
        .limit(5)
        .all()
    )
    weak_concepts = [row.concept for row in mastery_rows]

    configs = [
        {
            "name": "Full System",
            "description": "All components enabled (RAG + adaptive + weakness + mastery)",
            "context": full_context,
            "weak_concepts": weak_concepts,
            "adaptive": True,
        },
        {
            "name": "No Weakness Tracking",
            "description": "Adaptive mode ON but no weak concepts injected into prompt",
            "context": full_context,
            "weak_concepts": [],
            "adaptive": True,
        },
        {
            "name": "No Adaptive Mode",
            "description": "Baseline quiz generation without any adaptive targeting",
            "context": full_context,
            "weak_concepts": [],
            "adaptive": False,
        },
        {
            "name": "No RAG (Random Qs)",
            "description": "Quiz generated without document context (LLM general knowledge only)",
            "context": f"Generate quiz questions about: {request.topic or pdf.filename}",
            "weak_concepts": [],
            "adaptive": False,
        },
        {
            "name": "No Concept Mastery",
            "description": "RAG context used but mastery profile ignored, no adaptive weighting",
            "context": full_context,
            "weak_concepts": [],
            "adaptive": False,
        },
    ]

    results: list[dict] = []

    for cfg in configs:
        t0 = time.time()
        try:
            questions = await langchain_service.generate_quiz_with_agent(
                context=cfg["context"],
                topic=request.topic or f"content from {pdf.filename}",
                num_questions=request.num_questions,
                difficulty=request.difficulty,
                weak_concepts=cfg["weak_concepts"],
                adaptive_mode=cfg["adaptive"],
                model_name=model,
                temperature=request.temperature,
            )
        except Exception as e:
            logger.warning(f"Component ablation failed for '{cfg['name']}': {e}")
            questions = []

        elapsed = round((time.time() - t0) * 1000)

        results.append({
            "configuration": cfg["name"],
            "avg_score": len(questions) / request.num_questions * 100 if questions else 0,
            "questions_generated": len(questions),
            "generation_time_ms": elapsed,
            "description": cfg["description"],
        })

        await asyncio.sleep(2)

    return results


@router.get("/mastery-progression")
async def mastery_progression(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return quiz scores over time for mastery progression charting.
    Groups by quiz sequence number to show learning curve.
    """
    quizzes = (
        db.query(QuizModel)
        .filter(QuizModel.user_id == current_user.id, QuizModel.score.isnot(None))
        .order_by(QuizModel.completed_at.asc())
        .all()
    )

    baseline_series = []
    adaptive_series = []
    idx_b = 0
    idx_a = 0

    for q in quizzes:
        is_adaptive = bool(q.is_adaptive) or any(
            question.get("targeted", False) for question in (q.questions or [])
        )
        entry = {
            "quiz_id": str(q.id),
            "score": q.score,
            "topic": q.topic or "",
            "model": q.model_used or settings.GROQ_MODEL,
            "timestamp": q.completed_at.isoformat() if q.completed_at else None,
        }
        if is_adaptive:
            entry["seq"] = idx_a
            adaptive_series.append(entry)
            idx_a += 1
        else:
            entry["seq"] = idx_b
            baseline_series.append(entry)
            idx_b += 1

    return {"baseline": baseline_series, "adaptive": adaptive_series}
