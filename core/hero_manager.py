from core.hero import Hero


class HeroManager:
    def __init__(self, language="en"):
        self.language = language  # ✅ armazenamos o idioma atual

        # Carrega todos os heróis do idioma escolhido
        self.all_heroes = Hero.load_heroes(language=self.language)

        # Conjunto de IDs desbloqueados
        self.unlocked_heroes = set()

        # Desbloqueia os heróis iniciais
        for hero in self.all_heroes:
            if not hero.unlock_by_quest and hero.available_from_turn in (None, 0):
                self.unlocked_heroes.add(hero.id)

    def check_hero_unlocks(self, completed_quests: set[int], current_turn: int):
        """
        Atualiza desbloqueios e remoções de heróis baseado nas quests completadas
        e no turno atual.
        """
        for hero in self.all_heroes:
            # --- Remoção: se completou uma quest que faz o herói ir embora ---
            if any(q in completed_quests for q in hero.leave_on_quest):
                if hero.id in self.unlocked_heroes:
                    self.unlocked_heroes.remove(hero.id)
                continue

            # --- Desbloqueio ---
            if hero.unlock_by_quest:
                if all(q in completed_quests for q in hero.unlock_by_quest) \
                   and (hero.available_from_turn is None or current_turn >= hero.available_from_turn):
                    self.unlocked_heroes.add(hero.id)
            else:
                # heróis sem requisito de quest, mas com turno mínimo
                if hero.available_from_turn is not None and current_turn >= hero.available_from_turn:
                    self.unlocked_heroes.add(hero.id)

    def get_available_heroes(self) -> list[Hero]:
        """Retorna os heróis desbloqueados e disponíveis (status = idle)."""
        return [
            h for h in self.all_heroes
            if h.id in self.unlocked_heroes and h.status == "idle"
        ]

    def is_hero_unlocked(self, hero_id: int) -> bool:
        """Verifica se um herói está desbloqueado."""
        return hero_id in self.unlocked_heroes

    def get_hero_by_id(self, hero_id: int) -> Hero | None:
        """Busca um herói pelo ID."""
        for h in self.all_heroes:
            if h.id == hero_id:
                return h
        return None

    def get_hero_by_name(self, name: str) -> Hero | None:
        """Busca um herói pelo nome (case insensitive)."""
        name = name.strip().lower()
        for h in self.all_heroes:
            if h.name.strip().lower() == name:
                return h
        return None

    def reset_heroes(self):
        """Reseta o progresso dos heróis (para novo jogo, por exemplo)."""
        self.unlocked_heroes = set()
        for hero in self.all_heroes:
            hero.xp = 0
            hero.status = "idle"

    def reload_language(self, new_language: str):
        """Troca o idioma dos heróis em tempo real."""
        self.language = new_language
        self.all_heroes = Hero.load_heroes(language=new_language)
        # ⚠️ Mantém progresso e unlocks já existentes, se desejar resetar, chame reset_heroes()

    def load_heroes(self, language: str = "en"):
        from core.hero import Hero
        self.language = language
        self.heroes = Hero.load_heroes(language)
        print(f"🦸 Heróis carregados no idioma: {language}")


if __name__ == "__main__":
    manager = HeroManager(language="en")
    hero = manager.get_available_heroes()
    print(hero)
