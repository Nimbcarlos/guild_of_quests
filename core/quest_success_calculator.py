# quest_success_calculator.py

import random
from core.hero import Hero
from core.quest import Quest
from core.language_manager import LanguageManager


PERK_ATTRIBUTE_MAP = {
    # 🗡️ Furtividade / crime
    "stealth": "dexterity",      # furtividade
    "thievery": "dexterity",     # ladinagem

    # 🌿 Exploração / natureza
    "survival": "wisdom",        # sobrevivência
    "nature": "wisdom",          # natureza / druidismo

    # 🧪 Conhecimento técnico
    "alchemy": "intelligence",   # alquimia
    "arcana": "intelligence",    # arcanista
    "investigation": "intelligence",    # arcanista

    # 🗣️ Social
    "diplomacy": "wisdom",       # diplomacia
    "intimidation": "strength",  # intimidação

    # ✝️ Fé / suporte
    "cure": "wisdom",         # cura
    "religion": "wisdom",        # religião / exorcismo

    # ⛏️ Profissões físicas
    "mining": "strength",        # mineração
    "blacksmith": "strength",    # ferraria
    "athletics": "strength",     # atletismo
}

class QuestSuccessCalculator:
    def __init__(self, language_manager=None):
        """
        language_manager: instância do LanguageManager para fazer mapeamento reverso
        """
        self.lm = language_manager
    
    def calculate_success_chance(self, heroes: list[Hero], quest: Quest) -> float:
        if not heroes:
            return 0.0

        total_rating = 0
        quest_types = quest.type if isinstance(quest.type, list) else [quest.type]

        # 🔥 COMBATE
        if "fight" in quest_types:
            for hero in heroes:
                best_combat = max(
                    hero.stats.get(attr, 0)
                    for attr in ["strength", "dexterity", "intelligence", "wisdom"]
                )
                print("best_combat", best_combat)
                total_rating += best_combat
                print("total_rating", total_rating)

        # 🧠 SKILL / PERK
        else:
            for hero in heroes:
                best_value = 0

                for perk in getattr(hero, "perks", []):
                    if perk not in quest_types:
                        continue

                    attribute = PERK_ATTRIBUTE_MAP.get(perk)
                    if not attribute:
                        continue

                    value = hero.stats.get(attribute, 0)
                    best_value = max(best_value, value)

                total_rating += best_value

        # ⚖️ Fórmula base
        base_chance = total_rating / (quest.difficulty * 2)

        # ═══════════════════════════════════════
        # 🤝 SINERGIA DE ROLES
        # ═══════════════════════════════════════
        roles = [getattr(hero, "role", None) for hero in heroes]
        party_size = quest.max_heroes

        synergy_multiplier = 1.0

        def has(role, n=1):
            return roles.count(role) >= n

        if party_size == 2:
            if ("tank" in roles or "healer" in roles) and "dps" in roles:
                synergy_multiplier += 1
            else:
                synergy_multiplier -= 1

        elif party_size >= 3:
            if (
                roles.count("tank") >= 1 and
                roles.count("healer") >= 1 and
                roles.count("dps") >= 1
            ):
                synergy_multiplier += 1
            else:
                synergy_multiplier -= 1

        elif party_size >= 4:
            if (
                roles.count("tank") >= 1 and
                roles.count("healer") >= 1 and
                roles.count("dps") >= 2
            ):
                synergy_multiplier += 1
            else:
                synergsynergy_multipliery_penalty -= 1

        base_chance *= synergy_multiplier
        print(f"base_chance: {base_chance * 100:.1f}%")
        print(f"synergy_bonus: {synergy_multiplier * 100:.1f}%")

        return max(0.05, min(0.95, base_chance))

def run_mission_roll(success_chance: float) -> str:
    """
    Simula uma rolagem de dados e retorna o resultado traduzido:
    'critical', 'success', 'failure' ou 'critical_failure'.
    """
    lm = LanguageManager()  # lê o idioma atual
    roll = random.random()

    # 🔹 Determina resultado “interno” (em inglês, padrão de chave)
    if success_chance >= 0.9 and roll > 0.95:
        result_key = "success" # "critical"
    elif success_chance < 0.2 and roll < 0.05:
        result_key = "failure" # "critical_failure"
    elif roll < success_chance:
        result_key = "success"
    else:
        result_key = "failure"

    # 🔹 Traduz o texto conforme o idioma atual
    return result_key


# Funções standalone para compatibilidade com código antigo
_global_calculator = None

def calculate_success_chance(heroes: list[Hero], quest: Quest, language_manager=None) -> float:
    """Função standalone para compatibilidade"""
    global _global_calculator
    if _global_calculator is None or language_manager is not None:
        _global_calculator = QuestSuccessCalculator(language_manager)
    return _global_calculator.calculate_success_chance(heroes, quest)


if __name__ == "__main__":
    # Teste
    from unittest.mock import Mock
    
    hero = Mock()
    hero.stats = {"strength": 1, "dexterity": 4, "intelligence": 1, "wisdom": 1}
    
    quest = Mock()
    quest.type = "strength"  # em português
    quest.difficulty = 1.5
    
    # Teste sem LanguageManager
    print("=== Teste sem LanguageManager ===")
    calculator = QuestSuccessCalculator()
    chance = calculator.calculate_success_chance([hero], quest)
    print(f"Chance de sucesso: {chance * 100:.1f}%") 

    quest2 = Mock()
    quest2.type = "fight"  # em português
    quest2.difficulty = 0.4005
    
    # Teste sem LanguageManager
    print("=== Teste sem LanguageManager ===")
    calculator = QuestSuccessCalculator()
    chance = calculator.calculate_success_chance([hero], quest2)
    print(f"Chance de sucesso: {chance * 100:.1f}%") 
