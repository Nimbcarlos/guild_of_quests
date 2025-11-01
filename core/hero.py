import json
from pathlib import Path
from typing import Dict, List, Optional


def get_level_from_xp(xp: int) -> int:
    level = 1
    need = 100
    while xp >= need:
        xp -= need
        level += 1
        need += 100
    return level


class Hero:
    def __init__(
        self,
        id: int,
        name,
        hero_class,
        status: str,
        perks,
        defects,
        story,
        photo_url: str,
        photo_body_url: str,
        unlock_by_quest,
        available_from_turn: int,
        leave_on_quest,
        growth_curve: Dict[str, Dict[str, int]],
        starter: bool = False,
        xp: int = 0,
        language: str = "en"
    ):
        """Inicializa o herói já traduzindo com base no idioma."""
        self.id = id
        self.language = language

        # Campos que podem ser multilíngues
        self.name = self._get_lang_value(name)
        self.hero_class = self._get_lang_value(hero_class)
        self.story = self._get_lang_value(story)

        self.perks = self._get_lang_list(perks)
        self.defects = self._get_lang_list(defects)

        # Campos fixos
        self.status = 'idle'
        self.photo_url = photo_url
        self.photo_body_url = photo_body_url
        self.unlock_by_quest = unlock_by_quest or []
        self.available_from_turn = available_from_turn
        self.leave_on_quest = leave_on_quest or []
        self.growth_curve = growth_curve
        self.starter = starter
        self.xp = xp

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

    # -------------------- Métodos principais --------------------

    @property
    def level(self) -> int:
        return get_level_from_xp(self.xp)

    @property
    def stats(self) -> Dict[str, int]:
        return self.growth_curve.get(str(self.level), {}) or {}

    def get_attr(self, attr: str) -> int:
        return int(self.stats.get(attr, 0))

    def add_xp(self, amount: int) -> None:
        self.xp = max(0, self.xp + int(amount))

    def to_dict_min(self) -> Dict[str, object]:
        return {"id": self.id, "name": self.name, "xp": self.xp}

    def __str__(self) -> str:
        return (
            f"--- Ficha do Herói ---\n"
            f"Nome: {self.name}\n"
            f"Classe: {self.hero_class}\n"
            f"Nível: {self.level} (XP: {self.xp})\n"
            f"Perks: {', '.join(self.perks) if self.perks else '—'}\n"
            f"Defeitos: {', '.join(self.defects) if self.defects else '—'}\n"
            f"Atributos: {self.stats}\n"
        )

    # -------------------- Carregamento --------------------

    @staticmethod
    def load_heroes(language="en") -> list["Hero"]:
        """Carrega todos os heróis com o idioma especificado."""
        file_path = Path("data/heroes.json")
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo {file_path} não encontrado.")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [Hero(language=language, **hero_data) for hero_data in data]

    @staticmethod
    def get_hero_by_id(hero_id: int, language="en") -> Optional["Hero"]:
        for h in Hero.load_heroes(language):
            if h.id == hero_id:
                return h
        return None

    @staticmethod
    def get_hero_by_name(name: str, language="en") -> Optional["Hero"]:
        name = name.strip().lower()
        for h in Hero.load_heroes(language):
            if h.name.strip().lower() == name:
                return h
        return None


if __name__ == "__main__":
    hero = Hero.get_hero_by_id(1, language="en")
    print(hero)
