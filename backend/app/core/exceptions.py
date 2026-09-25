class InvalidStateTransitionError(Exception):
    """Lançada quando ocorre uma tentativa de transição ilegal na FSM."""
    def __init__(self, current_state: str, trigger: str):
        self.current_state = current_state
        self.trigger = trigger
        super().__init__(
            f"Transição inválida: Não é permitido disparar o evento '{trigger}' estando no estado '{current_state}'."
        )
