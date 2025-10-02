"""SQLAlchemy models for the problem database."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.sql import text

Base = declarative_base()


class Problem(Base):
    """Core problem entity."""
    
    __tablename__ = "problems"
    
    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    pg_source: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    metadata_items: Mapped[List["ProblemMetadata"]] = relationship(
        "ProblemMetadata", back_populates="problem", cascade="all, delete-orphan"
    )
    types: Mapped[List["ProblemType"]] = relationship(
        "ProblemType", back_populates="problem", cascade="all, delete-orphan"
    )
    subjects: Mapped[List["ProblemSubject"]] = relationship(
        "ProblemSubject", back_populates="problem", cascade="all, delete-orphan"
    )
    categories: Mapped[List["ProblemCategory"]] = relationship(
        "ProblemCategory", back_populates="problem", cascade="all, delete-orphan"
    )
    keywords: Mapped[List["ProblemKeyword"]] = relationship(
        "ProblemKeyword", back_populates="problem", cascade="all, delete-orphan"
    )
    macros: Mapped[List["ProblemMacro"]] = relationship(
        "ProblemMacro", back_populates="problem", cascade="all, delete-orphan"
    )
    documentation: Mapped[List["ProblemDocumentation"]] = relationship(
        "ProblemDocumentation", back_populates="problem", cascade="all, delete-orphan"
    )
    embeddings: Mapped[List["ProblemEmbedding"]] = relationship(
        "ProblemEmbedding", back_populates="problem", cascade="all, delete-orphan"
    )
    relations: Mapped[List["ProblemRelation"]] = relationship(
        "ProblemRelation", 
        foreign_keys="ProblemRelation.problem_id",
        back_populates="problem", 
        cascade="all, delete-orphan"
    )
    related_problems: Mapped[List["ProblemRelation"]] = relationship(
        "ProblemRelation",
        foreign_keys="ProblemRelation.related_problem_id", 
        back_populates="related_problem",
        cascade="all, delete-orphan"
    )


class ProblemMetadata(Base):
    """Key-value metadata for problems."""
    
    __tablename__ = "problem_metadata"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    problem: Mapped["Problem"] = relationship("Problem", back_populates="metadata_items")


class ProblemType(Base):
    """Problem types (sample, technique, snippet)."""
    
    __tablename__ = "problem_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    problem: Mapped["Problem"] = relationship("Problem", back_populates="types")
    
    __table_args__ = (UniqueConstraint("problem_id", "type"),)


class ProblemSubject(Base):
    """Problem subjects (algebra, calculus, etc.)."""
    
    __tablename__ = "problem_subjects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    subject: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    problem: Mapped["Problem"] = relationship("Problem", back_populates="subjects")
    
    __table_args__ = (UniqueConstraint("problem_id", "subject"),)


class ProblemCategory(Base):
    """Problem categories (inequality, proof, etc.)."""
    
    __tablename__ = "problem_categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    problem: Mapped["Problem"] = relationship("Problem", back_populates="categories")
    
    __table_args__ = (UniqueConstraint("problem_id", "category"),)


class ProblemKeyword(Base):
    """Problem keywords/tags."""
    
    __tablename__ = "problem_keywords"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    keyword: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    problem: Mapped["Problem"] = relationship("Problem", back_populates="keywords")
    
    __table_args__ = (UniqueConstraint("problem_id", "keyword"),)


class ProblemMacro(Base):
    """Required macros for problems."""
    
    __tablename__ = "problem_macros"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    macro: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    problem: Mapped["Problem"] = relationship("Problem", back_populates="macros")
    
    __table_args__ = (UniqueConstraint("problem_id", "macro"),)


class ProblemRelation(Base):
    """Related problems."""
    
    __tablename__ = "problem_relations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    related_problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    relation_type: Mapped[str] = mapped_column(String(50), default="see_also")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    problem: Mapped["Problem"] = relationship("Problem", foreign_keys=[problem_id], back_populates="relations")
    related_problem: Mapped["Problem"] = relationship("Problem", foreign_keys=[related_problem_id], back_populates="related_problems")
    
    __table_args__ = (UniqueConstraint("problem_id", "related_problem_id", "relation_type"),)


class ProblemDocumentation(Base):
    """Problem documentation sections."""
    
    __tablename__ = "problem_documentation"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    section: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    problem: Mapped["Problem"] = relationship("Problem", back_populates="documentation")
    
    __table_args__ = (UniqueConstraint("problem_id", "section"),)


class ProblemEmbedding(Base):
    """Vector embeddings for semantic search."""
    
    __tablename__ = "problem_embeddings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[str] = mapped_column(String(255), ForeignKey("problems.id", ondelete="CASCADE"))
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'statement', 'solution', 'description', 'full_text'
    embedding: Mapped[bytes] = mapped_column(Text, nullable=False)  # Vector embedding as JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    problem: Mapped["Problem"] = relationship("Problem", back_populates="embeddings")
    
    __table_args__ = (UniqueConstraint("problem_id", "content_type"),)


# Database configuration
def create_database_engine(database_url: str = "sqlite:///problems.db"):
    """Create SQLAlchemy engine with sqlite-vec support."""
    engine = create_engine(
        database_url,
        echo=False,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )
    
    # Enable sqlite-vec extension
    if "sqlite" in database_url:
        with engine.connect() as conn:
            conn.execute(text("SELECT load_extension('sqlite-vec')"))
    
    return engine


def create_session_factory(engine):
    """Create session factory."""
    return sessionmaker(bind=engine, expire_on_commit=False)


def init_database(engine):
    """Initialize database with all tables."""
    Base.metadata.create_all(bind=engine)
