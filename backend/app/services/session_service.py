from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.session import StudySessionModel


class SessionService:
    @staticmethod
    async def create_session(
        db: AsyncSession,
        session_uuid: str,
        topic: str,
        persona_id: str,
        focus_duration_minutes: int,
        turns_executed: int = 0,
        ai_feedback_summary: Optional[str] = None
    ) -> StudySessionModel:
        """Cria e persiste o registro consolidado de uma sessão de estudo."""
        session_record = StudySessionModel(
            session_uuid=session_uuid,
            topic=topic,
            persona_id=persona_id,
            focus_duration_minutes=focus_duration_minutes,
            turns_executed=turns_executed,
            ai_feedback_summary=ai_feedback_summary
        )
        db.add(session_record)
        await db.commit()
        await db.refresh(session_record)
        return session_record

    @staticmethod
    async def list_recent_sessions(db: AsyncSession, limit: int = 10):
        """Retorna as últimas sessões concluídas para o painel de histórico."""
        stmt = select(StudySessionModel).order_by(StudySessionModel.created_at.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()