from app.services.context_engine import ContextEngine


def test_engine():
    topic = "Estruturas de Dados: Tabelas Hash e Tratamento de Colisões"
    persona_id = "socratic_mentor"

    instruction = ContextEngine.build_system_instruction(topic, persona_id)
    greeting = ContextEngine.get_initial_greeting_prompt(topic, persona_id)
    tools = ContextEngine.get_tool_declarations()

    print("=== PROMPT DE SISTEMA COMPILADO ===")
    print(instruction)
    print("\n=== PROMPT DE ABERTURA ATIVA ===")
    print(greeting)
    print("\n=== FERRAMENTA REGISTRADA ===")
    print(tools[0]["name"], "->", tools[0]["description"][:60], "...")

    assert "Tabelas Hash" in instruction
    assert "extend_focus_time" in tools[0]["name"]
    assert len(tools) == 1
    print("\n✅ ContextEngine validado com sucesso!")


if __name__ == "__main__":
    test_engine()