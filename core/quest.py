import json
from pathlib import Path
from typing import List, Dict, Optional

class Quest:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        type: str,
        recommendedLevel: int,
        duration: int,
        difficulty: int,
        rewards: Dict[str, int],
        required_quests: List[str],
    ):
        self.id = id
        self.name = name
        self.description = description
        self.type = type
        self.recommended_level = recommendedLevel
        self.duration = duration
        self.difficulty = difficulty
        self.rewards = rewards
        self.required_quests = required_quests

        # Novo: turnos restantes
        self.remaining_turns = duration  

    def __str__(self) -> str:
        return (
            f"Id: {self.id}\n"
            f"Quest: {self.name}\n"
            f"Descrição: {self.description}\n"
            f"Tipo: {self.type}\n"
            f"Level Recomendado: {self.recommended_level}\n"
            f"Duração: {self.duration} turnos\n"
            f"Turnos Restantes: {self.remaining_turns}\n"
            f"Dificuldade: {self.difficulty}\n"
            f"Recompensas: {self.rewards}\n"
            f"Pré-requisitos: {', '.join(self.required_quests) if self.required_quests else 'Nenhum'}"
        )

    @staticmethod
    def load_quests(file_path: str = "data/quests.json") -> List["Quest"]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo {file_path} não encontrado.")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [Quest(**quest_data) for quest_data in data]

    @staticmethod
    def get_quest_by_name(name: str, file_path: str = "data/quests.json") -> Optional["Quest"]:
        quests = Quest.load_quests(file_path)
        for q in quests:
            if q.name.lower() == name.lower():
                return q
        return None
