from core.hero import Hero

class HeroManager:
    def __init__(self):
        # Carregar heróis do catálogo
        self.all_heroes = Hero.load_heroes()

        # Set com IDs de heróis desbloqueados
        self.unlocked_heroes = set()

        # Liberar automaticamente quem tem unlock_by_quest vazio
        for hero in self.all_heroes:
            if not hero.unlock_by_quest:  # se lista estiver vazia
                self.unlocked_heroes.add(hero.id)

    def check_hero_unlocks(self, completed_quests: set[int]):
        """
        Verifica quais heróis ficam disponíveis após progresso em quests.
        Se o herói tem unlock_by_quest vazio, ele já foi liberado no __init__.
        """
        for hero in self.all_heroes:
            if not hero.unlock_by_quest:
                continue  # já foi liberado no __init__

            # Se TODAS as quests necessárias estão em completed_quests, desbloqueia
            if all(q in completed_quests for q in hero.unlock_by_quest):
                self.unlocked_heroes.add(hero.id)

class HeroManager:
    def __init__(self):
        self.all_heroes = Hero.load_heroes()
        self.unlocked_heroes = set()

        for hero in self.all_heroes:
            if not hero.unlock_by_quest and hero.available_from_turn in (None, 0):
                self.unlocked_heroes.add(hero.id)

    def check_hero_unlocks(self, completed_quests: set[int], current_turn: int):
        """
        Atualiza unlocks e removals de heróis baseado em quests e turnos.
        """
        for hero in self.all_heroes:
            # --- Remoção: se alguma quest de leave foi concluída, expulsa ---
            if any(q in completed_quests for q in hero.leave_on_quest):
                if hero.id in self.unlocked_heroes:
                    self.unlocked_heroes.remove(hero.id)
                continue

            # --- Unlock: verifica turno e quests necessárias ---
            if hero.unlock_by_quest:
                if all(q in completed_quests for q in hero.unlock_by_quest) \
                   and (hero.available_from_turn is None or current_turn >= hero.available_from_turn):
                    self.unlocked_heroes.add(hero.id)
            else:
                # heróis sem unlock_by_quest mas com restrição de turno
                if hero.available_from_turn is not None and current_turn >= hero.available_from_turn:
                    self.unlocked_heroes.add(hero.id)

    def get_available_heroes(self) -> list[Hero]:
        """Retorna objetos Hero desbloqueados e disponíveis (idle)."""
        return [
            h for h in self.all_heroes
            if h.id in self.unlocked_heroes and h.status == "idle"
        ]

    def is_hero_unlocked(self, hero_id: int) -> bool:
        return hero_id in self.unlocked_heroes

    def get_hero_by_id(self, hero_id: int) -> Hero | None:
        for h in self.all_heroes:
            if h.id == hero_id:
                return h
        return None

    def reset_heroes(self):
        self.unlocked_heroes = set()
        for hero in self.all_heroes:
            hero.xp = 0
            hero.status = "idle"


if __name__ == "__main__":
    heroes = HeroManager()
    print(heroes.get_hero_by_id(1).name)
