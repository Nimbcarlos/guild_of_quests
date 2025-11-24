import random
from core.hero import Hero
from core.quest import Quest
from core.language_manager import LanguageManager


# quest_success_calculator.py

class QuestSuccessCalculator:
    def __init__(self, language_manager=None):
        """
        language_manager: instância do LanguageManager para fazer mapeamento reverso
        """
        self.lm = language_manager
        
        # Mapeamento interno (sempre em inglês)
        self.attribute_mapping = {
            "fight": None,  # tratamento especial
            "strength": "strength",
            "dexterity": "dexterity",
            "intelligence": "intelligence",
            "wisdom": "wisdom"
        }
        
        # Chaves de tradução para cada tipo de quest
        # Essas chaves devem existir nos seus arquivos de tradução
        self.quest_type_keys = {
            "fight": "quest_type_fight",
            "strength": "quest_type_strength",
            "dexterity": "quest_type_dexterity",
            "intelligence": "quest_type_intelligence",
            "wisdom": "quest_type_wisdom"
        }
        
        # Cache de traduções reversas para performance
        self._reverse_cache = {}
    
    def _build_reverse_mapping(self):
        """
        Constrói um mapeamento reverso: tradução → ID interno
        Usa o LanguageManager para pegar todas as traduções de todos os idiomas
        """
        if not self.lm:
            return {}
        
        reverse_map = {}
        
        # Para cada tipo de quest e sua chave de tradução
        for internal_id, translation_key in self.quest_type_keys.items():
            # Pega a tradução em TODOS os idiomas suportados
            for lang in ["en", "pt", "es", "ru", "zh", "ja"]:
                try:
                    # Salva o idioma atual
                    current_lang = self.lm.current_language
                    
                    # Muda temporariamente para esse idioma
                    self.lm.current_language = lang
                    translated = self.lm.t(translation_key)
                    
                    # Adiciona ao mapeamento reverso (case-insensitive)
                    if translated:
                        reverse_map[translated.lower()] = internal_id
                    
                    # Restaura idioma original
                    self.lm.current_language = current_lang
                except:
                    pass
        
        # Adiciona também os IDs em inglês como fallback
        for internal_id in self.attribute_mapping.keys():
            reverse_map[internal_id.lower()] = internal_id
        
        return reverse_map
    
    def _normalize_quest_type(self, quest_type: str) -> str:
        """
        Converte o tipo da quest (que pode estar em qualquer idioma) para o ID interno em inglês.
        """
        if not quest_type:
            return "fight"  # fallback
        
        # Se não tem LanguageManager, assume que já está em inglês
        if not self.lm:
            return quest_type.lower()
        
        # Constrói o cache se ainda não existe
        if not self._reverse_cache:
            self._reverse_cache = self._build_reverse_mapping()
        
        # Busca no cache (case-insensitive)
        normalized = quest_type.lower().strip()
        return self._reverse_cache.get(normalized, normalized)
    
    def calculate_success_chance(self, heroes: list[Hero], quest: Quest) -> float:
        total_rating = 0
        
        # Normaliza o tipo da quest para inglês
        quest_type_normalized = self._normalize_quest_type(quest.type)
        
        if quest_type_normalized not in self.attribute_mapping:
            print(f"[AVISO] Tipo de missão desconhecido: '{quest.type}' (normalizado: '{quest_type_normalized}')")
            print(f"[AVISO] Tipos válidos: {list(self.attribute_mapping.keys())}")
            return 0.0

        # --- tratamento especial para luta ---
        if quest_type_normalized == "fight":
            # Combate pode usar múltiplos atributos
            combat_attributes = ["strength", "dexterity", "intelligence", "wisdom"]
            for hero in heroes:
                # pega o maior atributo de combate de cada herói
                hero_rating = max(hero.stats.get(attr, 0) for attr in combat_attributes)
                total_rating += hero_rating
        else:
            main_attribute = self.attribute_mapping[quest_type_normalized]
            for hero in heroes:
                hero_attribute = hero.stats.get(main_attribute, 0)
                total_rating += hero_attribute

        # --- chance base ---
        base_chance = total_rating / (quest.difficulty * 2)

        return max(0.0, min(1.0, base_chance))
    
    def clear_cache(self):
        """Limpa o cache de traduções reversas (útil ao trocar de idioma)"""
        self._reverse_cache = {}

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
    quest.difficulty = 0.202
    
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
