import json
from pathlib import Path
from typing import Dict, List, Optional
from app.models.persona import Persona, PersonasConfig


class PersonaManager:
    """Gerencia o ciclo de vida e leitura das personas pedagógicas do sistema."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            # Caminho relativo seguro até app/config/personas.json
            base_dir = Path(__file__).resolve().parent.parent
            self.config_path = base_dir / "config" / "personas.json"
        else:
            self.config_path = config_path

        self._personas_map: Dict[str, Persona] = {}
        self.default_persona_id: str = ""
        self.load_personas()

    def load_personas(self) -> None:
        """Carrega e valida o arquivo JSON usando o schema Pydantic."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado em: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        validated_config = PersonasConfig(**data)
        self.default_persona_id = validated_config.default_persona_id
        self._personas_map = {p.id: p for p in validated_config.personas}

    def get_persona(self, persona_id: Optional[str] = None) -> Persona:
        """Retorna uma persona pelo ID ou a padrão caso o ID seja None ou inexistente."""
        target_id = persona_id or self.default_persona_id
        persona = self._personas_map.get(target_id)
        if not persona:
            return self._personas_map[self.default_persona_id]
        return persona

    def list_available_personas(self) -> List[dict]:
        """Lista resumo das personas disponíveis para consumo do frontend."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "tone": p.tone,
                "max_turns": p.max_turns
            }
            for p in self._personas_map.values()
        ]


# Instância única em memória (Singleton pattern)
persona_manager = PersonaManager()