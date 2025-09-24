import json
from pathlib import Path
from typing import Dict, List, Optional


def get_level_from_xp(xp: int) -> int:
    """
    Exemplo simples: custo cumulativo por nível.
    Nível 1 -> 0 XP
    Subir para 2 -> +100
    Subir para 3 -> +200 (acumulado 300)
    Subir para 4 -> +300 (acumulado 600) ...
    """
    level = 1
    need = 100
    while xp >= need:
        xp -= need
        level += 1
        need += 100
    return level


class Hero:
    """
    Representa um herói de catálogo (definição fixa do jogo).
    Progresso (XP) vem do save e é aplicado fora deste módulo (via save_manager/HeroManager).
    """
    def __init__(
        self,
        id: int,
        name: str,
        hero_class: str,
        status: str,
        perks: List[str],
        defects: List[str],
        story: str,
        photo_url: str,
        unlock_by_quest: None,
        growth_curve: Dict[str, Dict[str, int]],
        starter: bool = False,
        xp: int = 0,  # será sobrescrito pelo save_manager quando carregar progresso
    ):
        self.id = id
        self.name = name
        self.hero_class = hero_class
        self.status = 'idle'
        self.perks = perks
        self.defects = defects
        self.story = story
        self.photo_url = photo_url
        self.unlock_by_quest = unlock_by_quest or []
        self.growth_curve = growth_curve  # stats absolutos por nível (chaves string)
        self.starter = starter
        self.xp = xp  # progresso (default 0)

    # nível é calculado com base no XP atual
    @property
    def level(self) -> int:
        return get_level_from_xp(self.xp)

    @property
    def stats(self) -> Dict[str, int]:
        """Atributos absolutos do nível atual conforme a growth_curve."""
        return self.growth_curve.get(str(self.level), {}) or {}

    def get_attr(self, attr: str) -> int:
        """Acesso seguro a um atributo (ex.: 'strength', 'dexterity', ...)."""
        return int(self.stats.get(attr, 0))

    def add_xp(self, amount: int) -> None:
        self.xp = max(0, self.xp + int(amount))

    def to_dict_min(self) -> Dict[str, object]:
        """Forma minimal para salvar no progresso (saves\save.json)."""
        return {"id": self.id, "name": self.name, "xp": self.xp}

    def __str__(self) -> str:
        return (
            f"--- Ficha do Herói ---\n"
            f"Nome: {self.name}\n"
            f"ID: {self.id}\n"
            f"Classe: {self.hero_class}\n"
            f"Nível: {self.level}  (XP: {self.xp})\n"
            f"Status: {self.status}\n"
            f"Perks: {', '.join(self.perks) if self.perks else '—'}\n"
            f"Defeitos: {', '.join(self.defects) if self.defects else '—'}\n"
            f"Atributos (lvl {self.level}): {self.stats}\n"
        )

    # ---------- utilidades de carga do catálogo ----------
    @staticmethod
    def load_heroes(file_path: str = "data\heroes.json") -> List["Hero"]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo {file_path} não encontrado.")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [Hero(**row) for row in data]

    @staticmethod
    def get_hero_by_id(hero_id: int, file_path: str = "data\heroes.json") -> Optional["Hero"]:
        for h in Hero.load_heroes(file_path):
            if h.id == hero_id:
                return h
        return None

    @staticmethod
    def get_hero_by_name(name: str, file_path: str = "data\heroes.json") -> Optional["Hero"]:
        name = name.strip().lower()
        for h in Hero.load_heroes(file_path):
            if h.name.strip().lower() == name:
                return h
        return None
