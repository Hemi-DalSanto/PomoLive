from typing import List
from pydantic import BaseModel, Field


class Persona(BaseModel):
    id: str = Field(..., description="Identificador único da persona")
    name: str = Field(..., description="Nome de exibição na interface")
    tone: str = Field(..., description="Descrição do tom pedagógico")
    system_instruction: str = Field(..., description="Instruções de sistema para a Gemini Live API")
    first_question_prompt: str = Field(..., description="Mensagem de abertura ativa da IA")
    max_turns: int = Field(default=3, ge=1, le=10, description="Teto de turnos de diálogo")


class PersonasConfig(BaseModel):
    default_persona_id: str
    personas: List[Persona]