import json
from datetime import datetime, timezone
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.fsm import StudySessionFSM
from app.core.exceptions import InvalidStateTransitionError
from app.models.fsm import SessionTrigger
from app.core.database import async_session_maker
from app.services.session_service import SessionService

router = APIRouter()


def create_envelope(event: str, session_id: str, payload: dict) -> dict:
    """Empacota a resposta do servidor no Envelope Pattern oficial."""
    return {
        "event": event,
        "session_id": session_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload
    }


class ActiveSessionTracker:
    """Mantém instâncias em memória de FSM e dados temporários por conexão."""
    def __init__(self):
        self.fsm_instances: Dict[str, StudySessionFSM] = {}
        self.session_data: Dict[str, dict] = {}

    def get_or_create_fsm(self, session_id: str) -> StudySessionFSM:
        if session_id not in self.fsm_instances:
            self.fsm_instances[session_id] = StudySessionFSM(session_id=session_id)
        return self.fsm_instances[session_id]

    def remove_session(self, session_id: str):
        self.fsm_instances.pop(session_id, None)
        self.session_data.pop(session_id, None)


tracker = ActiveSessionTracker()


@router.websocket("/ws/session")
async def session_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    current_session_id = None

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                await websocket.send_json(
                    create_envelope(
                        "ERROR",
                        current_session_id or "unknown",
                        {"code": "INVALID_JSON", "message": "Payload JSON malformado."}
                    )
                )
                continue

            event_name = data.get("event")
            session_id = data.get("session_id")
            payload = data.get("payload", {})

            if not event_name or not session_id:
                await websocket.send_json(
                    create_envelope(
                        "ERROR",
                        session_id or "unknown",
                        {"code": "MISSING_ENVELOPE_FIELDS", "message": "Campos 'event' e 'session_id' são obrigatórios."}
                    )
                )
                continue

            current_session_id = session_id
            fsm = tracker.get_or_create_fsm(session_id)

            # --- PROCESSAMENTO DE EVENTOS CONTRATUAIS ---
            try:
                if event_name == "SESSION_START":
                    previous_state = fsm.current_state.value
                    new_state = fsm.trigger(SessionTrigger.SESSION_START).value
                    tracker.session_data[session_id] = payload

                    await websocket.send_json(
                        create_envelope(
                            "SESSION_STATE_CHANGED",
                            session_id,
                            {"previous_state": previous_state, "current_state": new_state, "reason": "SESSION_START"}
                        )
                    )

                elif event_name == "TIMER_EXPIRED":
                    previous_state = fsm.current_state.value
                    new_state = fsm.trigger(SessionTrigger.TIMER_EXPIRED).value

                    await websocket.send_json(
                        create_envelope(
                            "SESSION_STATE_CHANGED",
                            session_id,
                            {"previous_state": previous_state, "current_state": new_state, "reason": "TIMER_EXPIRED"}
                        )
                    )
                elif event_name == "GEMINI_READY":
                    previous_state = fsm.current_state.value
                    new_state = fsm.trigger(SessionTrigger.GEMINI_READY).value

                    await websocket.send_json(
                        create_envelope(
                            "SESSION_STATE_CHANGED",
                            session_id,
                            {"previous_state": previous_state, "current_state": new_state, "reason": "GEMINI_READY"}
                        )
                    )

                elif event_name == "CHECKIN_COMPLETE_MANUAL":
                    previous_state = fsm.current_state.value
                    new_state = fsm.trigger(SessionTrigger.CHECKIN_COMPLETE_MANUAL).value

                    # Persistência no SQLite ao atingir PERSISTING
                    init_data = tracker.session_data.get(session_id, {})
                    async with async_session_maker() as db_session:
                        saved_record = await SessionService.create_session(
                            db=db_session,
                            session_uuid=session_id,
                            topic=init_data.get("topic", "Tópico não informado"),
                            persona_id=init_data.get("persona_id", "socratic_mentor"),
                            focus_duration_minutes=init_data.get("focus_duration_minutes", 25),
                            turns_executed=3,
                            ai_feedback_summary="Ciclo concluído com sucesso."
                        )

                    # Transição de PERSISTING -> BREAK
                    fsm.trigger(SessionTrigger.SESSION_SAVED)

                    await websocket.send_json(
                        create_envelope(
                            "SESSION_SAVED",
                            session_id,
                            {
                                "db_id": saved_record.id,
                                "topic": saved_record.topic,
                                "focus_minutes": saved_record.focus_duration_minutes,
                                "turns_executed": saved_record.turns_executed,
                                "summary": saved_record.ai_feedback_summary,
                                "break_duration_minutes": init_data.get("break_duration_minutes", 5)
                            }
                        )
                    )

                elif event_name == "SESSION_ABORT":
                    fsm.trigger(SessionTrigger.SESSION_ABORT)
                    tracker.remove_session(session_id)
                    await websocket.send_json(
                        create_envelope(
                            "SESSION_STATE_CHANGED",
                            session_id,
                            {"previous_state": "FOCUS", "current_state": "IDLE", "reason": "USER_ABORT"}
                        )
                    )

            except InvalidStateTransitionError as err:
                await websocket.send_json(
                    create_envelope(
                        "ERROR",
                        session_id,
                        {"code": "INVALID_STATE_TRANSITION", "message": str(err), "recoverable": True}
                    )
                )

    except WebSocketDisconnect:
        if current_session_id:
            tracker.remove_session(current_session_id)