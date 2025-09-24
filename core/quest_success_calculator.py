import random
from core.hero import Hero
from core.quest import Quest

# quest_success_calculator.py

def calculate_success_chance(heroes: list[Hero], quest: Quest) -> float:
    total_rating = 0
    
    attribute_mapping = {
        "Fight": "strength",
        "Scout": "dexterity",
        "Social": "charisma",
        "Rescue": "constitution",
        "Crafting": "intelligence",
        "Gather": "dexterity"
    }

    # agora compara direto com a string
    if quest.type not in attribute_mapping:
        print(f"Tipo de missão desconhecido: {quest.type}")
        return 0.0

    main_attribute = attribute_mapping[quest.type]

    for hero in heroes:
        hero_attribute = hero.stats.get(main_attribute, 0)
        total_rating += hero_attribute

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
