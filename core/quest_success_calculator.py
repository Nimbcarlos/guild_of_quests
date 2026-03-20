# quest_success_calculator.py

import random
from core.hero import Hero
from core.quest import Quest
from core.language_manager import LanguageManager


PERK_ATTRIBUTE_MAP = {
    # 🗡️ Furtividade / crime
    "stealth": "dexterity",      # furtividade
    "thievery": "dexterity",     # ladinagem
    "performance": "dexterity",   # performance artística

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
    "smithing": "strength",    # ferraria
    "engineering": "intelligence",    # ferraria
    "athletics": "strength",     # atletismo
}

class QuestSuccessCalculator:
    def __init__(self, language_manager=None):
        """
        language_manager: instância do LanguageManager para fazer mapeamento reverso
        """
        self.lm = language_manager
    
    def calculate_success_chance(self, heroes: list["Hero"], quest: "Quest") -> float:
        if not heroes:
            return 0.0

        total_rating = 0.0
        quest_types = quest.type if isinstance(quest.type, list) else [quest.type]

        # 🔥 COMBATE
        if "fight" in quest_types:
            for hero in heroes:
                best_combat = max(
                    hero.stats.get(attr, 0)
                    for attr in ["strength", "dexterity", "intelligence", "wisdom"]
                )
                total_rating += best_combat

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

        # ⚖️ Fórmula base (antes de sinergia)
        # Chance "crua" (vai ser clampada no final)
        base_chance = total_rating / (quest.difficulty * 2)

        # ═══════════════════════════════════════
        # 🤝 SINERGIA (corrigida e previsível)
        # ═══════════════════════════════════════
        roles = [getattr(hero, "role", None) for hero in heroes]
        party_size = quest.max_heroes
        n_sent = len(heroes)

        synergy_multiplier = 1.0

        # 1) SINERGIA DE ROLES: SOMENTE PARA FIGHT
        if "fight" in quest_types:
            # Regra suave: bônus pequeno se a composição esperada existe,
            # penalidade pequena se estiver faltando peça-chave.
            if party_size >= 4:
                has_core = (roles.count("tank") >= 1 and roles.count("healer") >= 1 and roles.count("dps") >= 2)
            elif party_size == 3:
                has_core = (roles.count("tank") >= 1 and roles.count("healer") >= 1 and roles.count("dps") >= 1)
            elif party_size == 2:
                has_core = (("tank" in roles or "healer" in roles) and ("dps" in roles))
            else:
                has_core = True  # solo: nada pra checar

            # bônus/penalidade leve (não destrói o balance)
            synergy_multiplier *= 1.15 if has_core else 0.85

            # Undercomp em fight: se mandou menos que o max, uma penalidade suave extra.
            # (mantém o "risco" do undercomp sem virar 5% automático)
            if n_sent < party_size:
                missing = party_size - n_sent
                synergy_multiplier *= (0.92 ** missing)  # -8% por herói faltando

        # 2) SINERGIA DE "COBERTURA" PARA SKILLS (ex.: performance + thievery)
    # 2) SINERGIA DE "COBERTURA" PARA SKILLS (ex.: performance + thievery)
        else:
            required_skills = [t for t in quest_types if t != "fight"]

            if len(required_skills) >= 2 and party_size >= 2:
                hero_skills = []
                for hero in heroes:
                    perks = set(getattr(hero, "perks", []))
                    hero_skills.append(set(req for req in required_skills if req in perks))

                # Cobertura total (ignorando distribuição)
                covered_all = set().union(*hero_skills) if hero_skills else set()
                full_coverage = all(req in covered_all for req in required_skills)

                # ===== Caso especial: quest de 2 skills desenhada pra 2 heróis =====
                if party_size == 2 and len(required_skills) == 2:
                    a, b = required_skills[0], required_skills[1]

                    # Quantos heróis cobrem cada skill
                    count_a = sum(1 for s in hero_skills if a in s)
                    count_b = sum(1 for s in hero_skills if b in s)

                    # Distribuição ideal: existe pelo menos um herói para A e um herói para B
                    distributed_ok = (count_a >= 1 and count_b >= 1)

                    # Mas queremos penalizar o caso "mandei 1 só herói", mesmo que ele cubra as duas
                    if len(heroes) == 1:
                        # Um só herói tentando fazer as duas funções (mesmo se cobrir A e B)
                        # Penalidade pra refletir simultaneidade/risco
                        if full_coverage:
                            synergy_multiplier *= 0.80
                        else:
                            synergy_multiplier *= 0.70

                    else:
                        # 2 heróis enviados (o esperado)
                        if distributed_ok:
                            # Se está distribuído, é o "jeito certo".
                            # Se um herói cobre ambos e o outro cobre pelo menos um, ainda conta como ok.
                            synergy_multiplier *= 1.10
                        else:
                            # Duplicou uma skill e faltou a outra: erro de composição
                            synergy_multiplier *= 0.75

                # ===== Caso geral: 3+ skills ou parties maiores =====
                else:
                    synergy_multiplier *= 1.10 if full_coverage else 0.90

                # Penalidade leve por undercomp em skill (faltou mão)
                if len(heroes) < party_size:
                    missing = party_size - len(heroes)
                    synergy_multiplier *= (0.95 ** missing)
                    
        base_chance *= synergy_multiplier

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
