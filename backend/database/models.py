"""
Database models for multi-user system
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, JSON, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from database.connection import Base


def _uuid_str() -> str:
    """Generate UUID string suitable for all databases (including SQLite)."""
    return str(uuid.uuid4())


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    # Use string IDs so the same models work on SQLite and PostgreSQL
    id = Column(String(36), primary_key=True, default=_uuid_str)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    pdfs = relationship("PDF", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="user", cascade="all, delete-orphan")
    weaknesses = relationship("Weakness", back_populates="user", cascade="all, delete-orphan")
    concept_mastery = relationship("ConceptMastery", back_populates="user", cascade="all, delete-orphan")


class PDF(Base):
    """PDF document model"""
    __tablename__ = "pdfs"
    
    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    file_id = Column(String(255), unique=True, index=True, nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
    total_chunks = Column(Integer, default=0)
    file_size = Column(Integer)  # in bytes
    
    # Relationships
    user = relationship("User", back_populates="pdfs")
    chats = relationship("Chat", back_populates="pdf", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="pdf", cascade="all, delete-orphan")


class Chat(Base):
    """Chat history model"""
    __tablename__ = "chats"
    
    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    pdf_id = Column(String(36), ForeignKey("pdfs.id"), nullable=False)
    messages = Column(JSON, default=list)  # [{role: "user/assistant", content: "...", timestamp: "..."}]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    pdf = relationship("PDF", back_populates="chats")


class Quiz(Base):
    """Quiz model"""
    __tablename__ = "quizzes"
    
    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    pdf_id = Column(String(36), ForeignKey("pdfs.id"), nullable=False)
    topic = Column(String(500))
    questions = Column(JSON)  # Quiz questions array
    user_answers = Column(JSON)  # User's answers
    score = Column(Float)  # Percentage score
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    model_used = Column(String(100), nullable=True)
    is_adaptive = Column(Integer, default=0)  # 0=baseline, 1=adaptive
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="quizzes")
    pdf = relationship("PDF", back_populates="quizzes")


class Weakness(Base):
    """User weakness tracking"""
    __tablename__ = "weaknesses"
    
    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    concept = Column(String(500), nullable=False)
    frequency = Column(Integer, default=1)
    last_incorrect_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="weaknesses")


class ConceptMastery(Base):
    """Per-user, per-concept mastery profile used by the adaptive pipeline"""
    __tablename__ = "concept_mastery"
    
    id = Column(String(36), primary_key=True, default=_uuid_str)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    concept = Column(String(500), nullable=False)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    mastery_score = Column(Float, default=0.0)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_pdf_id = Column(String(36), ForeignKey("pdfs.id"), nullable=True)
    
    user = relationship("User", back_populates="concept_mastery")
