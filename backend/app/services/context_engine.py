from typing import Any, Dict
from app.core.persona_loader import persona_manager
from app.models.persona import Persona


class ContextEngine:
    """Compila dinamicamente os prompts de sistema e configurações de ferramentas

    para a sessão com a Gemini Multimodal Live API.
    """

    SYSTEM_BASE_RULES = (
        "Você é um tutor de estudos por voz interativo no aplicativo PomoLive.\n"
        "REGRAS DE CONVERSAÇÃO ORAL:\n"
        "1. Suas respostas serão convertidas diretamente em áudio. Seja conciso: responda em NO MÁXIMO 2 ou 3 frases curtas.\n"
        "2. Fale exclusivamente em Português do Brasil de forma natural e sem jargões desnecessários.\n"
        "3. Seu objetivo é avaliar a retenção do estudante usando a Técnica Feynman: faça perguntas conceituais e abertas.\n"
        "4. Se o usuário solicitar mais tempo de foco antes de pausar (ex: 'preciso de mais 10 minutos', 'quero estudar mais um pouco'), "
        "invoque IMEDIATAMENTE a ferramenta `extend_focus_time` com a quantidade de minutos requisitada."
    )

    @classmethod
    def get_tool_declarations(cls) -> list[Dict[str, Any]]:
        """Retorna o esquema da ferramenta de extensão de tempo para a Live API."""
        return [
            {
                "name": "extend_focus_time",
                "description": (
                    "Estende o tempo do ciclo de foco atual quando o usuário pede por voz "
                    "mais tempo de estudo antes de ir para a pausa."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "additional_minutes": {
                            "type": "INTEGER",
                            "description": "Quantidade de minutos adicionais solicitados pelo estudante (ex: 5, 10, 15)."
                        }
                    },
                    "required": ["additional_minutes"]
                }
            }
        ]

    @classmethod
    def build_system_instruction(cls, topic: str, persona_id: str) -> str:
        """Monta o prompt de sistema final combinando regras operacionais, persona e tópico."""
        persona: Persona = persona_manager.get_persona(persona_id)

        instruction = (
            f"{cls.SYSTEM_BASE_RULES}\n\n"
            f"--- PERFIL DA PERSONA ({persona.name.upper()}) ---\n"
            f"Tom pedagógico: {persona.tone}.\n"
            f"Diretriz pedagógica: {persona.system_instruction}\n\n"
            f"--- CONTEXTO ATUAL DO ESTUDANTE ---\n"
            f"Tópico estudado neste ciclo: '{topic}'.\n"
            f"Diretriz de arguição: Avalie se o estudante compreendeu o essencial de '{topic}' sem decoreba."
        )
        return instruction

    @classmethod
    def get_initial_greeting_prompt(cls, topic: str, persona_id: str) -> str:
        """Prompt injetado para forçar a IA a tomar a palavra no início da checagem."""
        persona: Persona = persona_manager.get_persona(persona_id)
        return (
            f"{persona.first_question_prompt} "
            f"(Lembre-se: o estudante acabou de estudar sobre '{topic}')."
        )