"""
Learner Profile Service — maintains per-user concept mastery and exposes
helpers consumed by the quiz generator, chat router, and analytics router.
"""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from database.models import ConceptMastery, Weakness
from logging_config import get_logger

logger = get_logger(__name__)

MASTERY_WEAK_THRESHOLD = 0.4


class LearnerProfileService:

    # ------------------------------------------------------------------
    # Core mastery update (called after every quiz submission)
    # ------------------------------------------------------------------
    def update_mastery_from_quiz(
        self,
        db: Session,
        user_id: str,
        questions: List[dict],
        user_answers: dict,
        pdf_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Walk through each question, compare with user answers, and
        upsert the ConceptMastery row for the tagged concept.

        Returns a list of {"concept": ..., "mastery_score": ...} dicts.
        """
        updated: List[Dict] = []

        for q in questions:
            concept = (q.get("concept") or "").strip()
            if not concept:
                continue

            q_id = str(q["id"])
            correct_answer = q["correct_answer"]
            user_answer = (user_answers.get(q_id) or "").strip()
            is_correct = user_answer == correct_answer.strip()

            row = (
                db.query(ConceptMastery)
                .filter(
                    ConceptMastery.user_id == user_id,
                    ConceptMastery.concept == concept,
                )
                .first()
            )

            if row is None:
                row = ConceptMastery(
                    user_id=user_id,
                    concept=concept,
                    correct_count=0,
                    incorrect_count=0,
                    mastery_score=0.0,
                    source_pdf_id=pdf_id,
                )
                db.add(row)

            if is_correct:
                row.correct_count += 1
            else:
                row.incorrect_count += 1

            total = row.correct_count + row.incorrect_count
            row.mastery_score = round(row.correct_count / total, 3) if total else 0.0
            row.last_seen = datetime.utcnow()

            updated.append({"concept": concept, "mastery_score": row.mastery_score})

        db.flush()
        return updated

    # ------------------------------------------------------------------
    # Retrieve weak concepts for a user
    # ------------------------------------------------------------------
    def get_weak_concepts(
        self,
        db: Session,
        user_id: str,
        threshold: float = MASTERY_WEAK_THRESHOLD,
        limit: int = 10,
    ) -> List[Dict]:
        """Return concepts where mastery_score < threshold, sorted weakest-first."""
        rows = (
            db.query(ConceptMastery)
            .filter(
                ConceptMastery.user_id == user_id,
                ConceptMastery.mastery_score < threshold,
            )
            .order_by(ConceptMastery.mastery_score.asc())
            .limit(limit)
            .all()
        )
        return [
            {
                "concept": r.concept,
                "mastery_score": r.mastery_score,
                "correct": r.correct_count,
                "incorrect": r.incorrect_count,
                "last_seen": r.last_seen.isoformat() if r.last_seen else None,
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Full mastery profile for analytics / dashboard
    # ------------------------------------------------------------------
    def get_full_profile(
        self, db: Session, user_id: str
    ) -> List[Dict]:
        rows = (
            db.query(ConceptMastery)
            .filter(ConceptMastery.user_id == user_id)
            .order_by(ConceptMastery.mastery_score.asc())
            .all()
        )
        return [
            {
                "concept": r.concept,
                "mastery_score": r.mastery_score,
                "correct": r.correct_count,
                "incorrect": r.incorrect_count,
                "last_seen": r.last_seen.isoformat() if r.last_seen else None,
            }
            for r in rows
        ]

    # ------------------------------------------------------------------
    # Weakness summary suitable for injecting into LLM prompts
    # ------------------------------------------------------------------
    def weakness_summary_for_prompt(
        self, db: Session, user_id: str, limit: int = 5
    ) -> str:
        """Build a plain-text summary of weak concepts for LLM system prompts."""
        weak = self.get_weak_concepts(db, user_id, limit=limit)
        if not weak:
            return ""
        lines = [
            f"- {w['concept']} (mastery {w['mastery_score']:.0%}, "
            f"{w['incorrect']} wrong / {w['correct']} right)"
            for w in weak
        ]
        return (
            "The learner currently struggles with these concepts:\n"
            + "\n".join(lines)
        )

    # ------------------------------------------------------------------
    # Recommendations based on mastery data
    # ------------------------------------------------------------------
    def get_recommendations(
        self, db: Session, user_id: str
    ) -> Dict:
        weak = self.get_weak_concepts(db, user_id, limit=5)
        strong = (
            db.query(ConceptMastery)
            .filter(
                ConceptMastery.user_id == user_id,
                ConceptMastery.mastery_score >= 0.8,
            )
            .order_by(ConceptMastery.mastery_score.desc())
            .limit(5)
            .all()
        )
        return {
            "priority_review": [w["concept"] for w in weak],
            "strong_concepts": [s.concept for s in strong],
            "suggestion": (
                f"Focus on: {weak[0]['concept']}" if weak else "You're doing great — try harder quizzes!"
            ),
        }


learner_profile_service = LearnerProfileService()
