from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.core.database import Base


class StudySessionModel(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_uuid = Column(String(36), unique=True, index=True, nullable=False)
    topic = Column(String(255), nullable=False)
    persona_id = Column(String(50), nullable=False)
    focus_duration_minutes = Column(Integer, nullable=False)
    turns_executed = Column(Integer, default=0, nullable=False)
    ai_feedback_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)