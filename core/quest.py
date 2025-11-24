import json
from pathlib import Path
from typing import List, Dict, Optional


class Quest:
    def __init__(
        self,
        id: str,
        name,
        description,
        type: str,
        expired_at: int,
        available_from_turn: int,
        duration: int,
        difficulty: int,
        rewards: Dict[str, int],
        required_quests: List[str],
        forbidden_quests: List[str] = None,
        required_fail_quests: List[str] = None,
        required_heroes: List[str] = None,
        forbidden_heroes: List[str] = None,
        available_since_turn=None,
        language: str = "en",
    ):
        self.id = id
        self.language = language

        # 🔹 Traduz automaticamente name e description se forem dicionários
        self.name = self._get_lang_value(name)
        self.description = self._get_lang_value(description)

        self.type = type
        self.expired_at = expired_at
        self.available_from_turn = available_from_turn
        self.duration = duration
        self.difficulty = difficulty
        self.rewards = rewards
        self.required_quests = required_quests
        self.forbidden_quests = forbidden_quests
        self.required_fail_quests = required_fail_quests
        self.required_heroes = required_heroes or []
        self.forbidden_heroes = forbidden_heroes or []
        self.available_since_turn = available_since_turn

        self.remaining_turns = duration

    # -------------------- Métodos auxiliares --------------------

    def _get_lang_value(self, value):
        """Retorna o texto no idioma atual (ou o original se for string)."""
        if isinstance(value, dict):
            return value.get(self.language) or next(iter(value.values()))
        return value

    def _get_lang_list(self, value):
        """Retorna lista traduzida se houver versões por idioma."""
        if isinstance(value, dict):
            return value.get(self.language, [])
        return value or []

    def __str__(self) -> str:
        return (
            f"Id: {self.id}\n"
            f"Quest: {self.name}\n"
            f"Descrição: {self.description}\n"
            f"Tipo: {self.type}\n"
            f"Expira em: {self.expired_at}\n"
            f"Duração: {self.duration} turnos\n"
            f"Turnos Restantes: {self.remaining_turns}\n"
            f"Dificuldade: {self.difficulty}\n"
            f"Recompensas: {self.rewards}\n"
            f"Pré-requisitos: {', '.join(str(q) for q in self.required_quests) if self.required_quests else 'Nenhum'}"
            f"forbidden_quests: {', '.join(str(q) for q in self.forbidden_quests) if self.forbidden_quests else 'Nenhum'}"
            f"Failed Quests: {', '.join(str(q) for q in self.required_fail_quests) if self.required_fail_quests else 'Nenhum'}"
            f"Required Heroes: {', '.join(str(q) for q in self.required_heroes) if self.required_heroes else 'Nenhum'}"
            f"Forbidden Heroes: {', '.join(str(q) for q in self.forbidden_heroes) if self.forbidden_heroes else 'Nenhum'}"
            f"Iniciada no turno: {self.available_since_turn}"
        )

    def is_expired(self, current_turn: int) -> bool:
        if self.available_since_turn is None:
            return False
        return (current_turn - self.available_since_turn) >= self.expired_at

    # 🔹 Carrega quests de acordo com o idioma
    @staticmethod
    def load_quests(language="en") -> list["Quest"]:
        """Carrega todos os heróis com o idioma especificado."""
        file_path = Path("data/quests.json")
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo {file_path} não encontrado.")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [Quest(language=language, **quest_data ) for quest_data in data]

    @staticmethod
    def get_quest_by_name(name: str, language: str = "en") -> Optional["Quest"]:
        quests = Quest.load_quests(language)
        for q in quests:
            if q.name.lower() == name.lower():
                return q
        return None
