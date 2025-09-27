import random
from core.hero import Hero
from core.quest import Quest

# quest_success_calculator.py

def calculate_success_chance(heroes: list[Hero], quest: Quest) -> float:
    total_rating = 0
    
    attribute_mapping = {
        "Fight": None,  # tratamento especial abaixo
        "Scout": "dexterity",
        "Social": "charisma",
        "Rescue": "constitution",
        "Crafting": "intelligence",
        "Gather": "dexterity"
    }

    if quest.type not in attribute_mapping:
        print(f"Tipo de missão desconhecido: {quest.type}")
        return 0.0

    # --- tratamento especial para luta ---
    if quest.type == "Fight":
        # Combate pode usar múltiplos atributos
        combat_attributes = ["strength", "dexterity", "intelligence", "constitution"]
        for hero in heroes:
            # pega o maior atributo de combate de cada herói
            hero_rating = max(hero.stats.get(attr, 0) for attr in combat_attributes)
            total_rating += hero_rating
    else:
        main_attribute = attribute_mapping[quest.type]
        for hero in heroes:
            hero_attribute = hero.stats.get(main_attribute, 0)
            total_rating += hero_attribute

    # --- chance base ---
    base_chance = total_rating / (quest.difficulty * 10)

    return max(0.0, min(1.0, base_chance))


def run_mission_roll(success_chance: float) -> str:
    """
    Simula uma rolagem de dados para determinar o resultado da missão,
    incluindo sucesso crítico e falha crítica.
    Retorna "Crítico", "Sucesso", "Falha" ou "Falha Crítica".
    """
    roll = random.random()

    if success_chance >= 0.9 and roll > 0.95:
        return "Crítico"
    elif success_chance < 0.2 and roll < 0.05:
        return "Falha Crítica"
    elif roll < success_chance:
        return "Sucesso"
    else:
        return "Falha"
