from app.core.fsm import StudySessionFSM
from app.core.exceptions import InvalidStateTransitionError
from app.models.fsm import SessionState, SessionTrigger


def run_tests():
    fsm = StudySessionFSM(session_id="test-session-123")
    print("1. Estado inicial:", fsm.current_state)
    assert fsm.current_state == SessionState.IDLE

    # Transição legal: Iniciar foco
    new_state = fsm.trigger(SessionTrigger.SESSION_START)
    print("2. Após SESSION_START:", new_state)
    assert new_state == SessionState.FOCUS

    # Transição ilegal: Tentar acionar ferramenta de estender tempo sem estar na checagem
    try:
        fsm.trigger(SessionTrigger.EXTEND_TIME_TOOL_CALLED)
        assert False, "Deveria ter falhado com InvalidStateTransitionError"
    except InvalidStateTransitionError as e:
        print("3. Transição ilegal bloqueada com sucesso:", e)

    # Avançar fluxo completo até a checagem
    fsm.trigger(SessionTrigger.TIMER_EXPIRED)
    assert fsm.current_state == SessionState.CHECKIN_CONNECTING
    print("4. Timer expirou ->", fsm.current_state)

    fsm.trigger(SessionTrigger.GEMINI_READY)
    assert fsm.current_state == SessionState.ACTIVE_DISCUSSION
    print("5. Gemini conectado ->", fsm.current_state)

    # Testando Tool Calling de estender tempo (retorno ao FOCUS)
    fsm.trigger(SessionTrigger.EXTEND_TIME_TOOL_CALLED)
    assert fsm.current_state == SessionState.FOCUS
    print("6. Extensão de tempo solicitada por voz -> Retornou para:", fsm.current_state)

    print("\n✅ Todos os testes da FSM passaram com sucesso!")


if __name__ == "__main__":
    run_tests()