"""
SQLAlchemy ORM models for database tables.

Defines:
- Users table
- FaceEmbeddings table (for face recognition)
- Events (calendar) table
- Tasks table
- Messages table
- Memories table (with vector support)
"""

from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, Text, Enum, Integer, LargeBinary
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    PARENT = "parent"
    CHILD = "child"


class User(Base):
    """Family member."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    avatar_url = Column(String(500))
    preferences = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    events = relationship("Event", back_populates="user")
    tasks = relationship("Task", back_populates="assignee")
    memories = relationship("Memory", back_populates="user")
    face_embeddings = relationship("FaceEmbedding", back_populates="user")


class FaceEmbedding(Base):
    """Face encoding for recognition.

    Stores 128-dimensional face encodings from face_recognition library.
    Multiple encodings per user for robustness (different angles, lighting).
    """
    __tablename__ = "face_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    encoding = Column(ARRAY(Float), nullable=False)  # 128-dim face_recognition encoding
    source_image = Column(String(500))  # Optional: path to source image
    quality_score = Column(Float)  # Optional: face detection confidence
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="face_embeddings")


class Event(Base):
    """Calendar event."""
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    title = Column(String(500), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime)
    location = Column(String(500))
    notes = Column(Text)
    source = Column(String(50), default="local")  # local, cozi, etc.
    external_id = Column(String(100))  # ID from external source
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="events")


class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(Base):
    """Task or chore."""
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    due_date = Column(DateTime)
    completed_at = Column(DateTime)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    assignee = relationship("User", back_populates="tasks")


class Message(Base):
    """Conversation message."""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    role = Column(String(20), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Memory(Base):
    """Long-term memory with vector embedding."""
    __tablename__ = "memories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    memory_type = Column(String(50), nullable=False)  # observation, fact, preference
    embedding = Column(Vector(384))  # MiniLM-L6-v2 dimension
    importance = Column(Float, default=0.5)
    access_count = Column(Float, default=0)
    last_accessed = Column(DateTime)
    metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="memories")
