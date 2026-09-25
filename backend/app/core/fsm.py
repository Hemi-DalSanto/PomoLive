import json
from pathlib import Path
from typing import Dict, Optional, Set, Tuple
from app.core.exceptions import InvalidStateTransitionError
from app.models.fsm import SessionState, SessionTrigger


class StudySessionFSM:
    """Máquina de Estados Finita para governança do ciclo Pomodoro e checagem de voz."""

    def __init__(self, session_id: str, transitions_path: Optional[Path] = None):
        self.session_id = session_id
        
        if transitions_path is None:
            # Caminho relativo: backend/app/core -> raiz PomoLive -> shared/fsm/transitions.json
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            self.transitions_path = base_dir / "shared" / "fsm" / "transitions.json"
        else:
            self.transitions_path = transitions_path

        # Tabela de transições no formato: (estado_origem, gatilho) -> estado_destino
        self._transitions_table: Dict[Tuple[str, str], str] = {}
        self.current_state: SessionState = SessionState.IDLE
        
        self._load_rules()

    def _load_rules(self) -> None:
        """Carrega e indexa as regras do transitions.json."""
        if not self.transitions_path.exists():
            raise FileNotFoundError(f"Arquivo FSM não encontrado em: {self.transitions_path}")

        with open(self.transitions_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for rule in data.get("transitions", []):
            origin = rule["from"]
            trigger = rule["trigger"]
            target = rule["to"]
            self._transitions_table[(origin, trigger)] = target

    def can_transition(self, trigger: SessionTrigger) -> bool:
        """Verifica se um gatilho é legal a partir do estado atual."""
        return (self.current_state.value, trigger.value) in self._transitions_table

    def trigger(self, trigger: SessionTrigger) -> SessionState:
        """Executa a transição de estado se for legal, caso contrário lança erro."""
        key = (self.current_state.value, trigger.value)
        if key not in self._transitions_table:
            raise InvalidStateTransitionError(
                current_state=self.current_state.value,
                trigger=trigger.value
            )

        previous_state = self.current_state
        self.current_state = SessionState(self._transitions_table[key])
        return self.current_state

    def force_error_state(self) -> SessionState:
        """Transiciona de forma segura para ERROR em caso de exceções não previstas."""
        self.current_state = SessionState.ERROR
        return self.current_state