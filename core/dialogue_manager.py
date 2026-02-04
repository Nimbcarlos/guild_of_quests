# core/dialogue_manager.py
import json
import random
import os
from core.language_manager import LanguageManager


class DialogueManager:
    def __init__(self, language="en"):
        self.language = language
        self.lm = LanguageManager()
        self.heroes_folder = "data/heroes/dialogues"

    def set_language(self, language):
        self.language = language

    def _load_hero_dialogue(self, hero_id: str) -> dict:
        path = os.path.join(self.heroes_folder, f"{hero_id}.json")
        
        if not os.path.exists(path):
            print(f"[DialogueManager] Arquivo de diálogos não encontrado: {path}")
            return {}
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DialogueManager] Erro ao carregar {path}: {e}")
            return {}

    def show_quest_dialogue(self, heroes: list, quest_id: str, result: str) -> list:
        quest_id = str(quest_id)
        result = result.lower()

        ROLE_ORDER = {
            "tank": 0,
            "dps": 1,
            "healer": 2
        }

        # Ordena heróis pela ordem narrativa desejada
        ordered_heroes = sorted(
            heroes,
            key=lambda h: ROLE_ORDER.get((h.role or "").lower(), 99)
        )

        party_ids = {str(h.id) for h in heroes}
        falas = []

        for hero in ordered_heroes:
            hero_id = str(hero.id)

            hero_data = self._load_hero_dialogue(hero_id)
            if not hero_data:
                continue

            quest_block = hero_data.get("quests", {}).get(quest_id)
            if not quest_block:
                continue

            result_block = quest_block.get(result)
            if not result_block:
                continue

            chosen_text = None

            # Relações específicas
            for other_hero_id in party_ids:
                if other_hero_id == hero_id:
                    continue

                lang_block = result_block.get(other_hero_id, {})
                texts = lang_block.get(self.language)

                if isinstance(texts, list) and texts:
                    chosen_text = random.choice(texts)
                    break

            # Texto base
            if not chosen_text:
                base_block = result_block.get("text", {})
                base_texts = base_block.get(self.language)

                if isinstance(base_texts, list) and base_texts:
                    chosen_text = random.choice(base_texts)

            if chosen_text:
                falas.append({
                    "id": hero_id,
                    "text": chosen_text
                })

        if not falas:
            return [{
                "id": "assistant",
                "text": self.lm.t("assistant_fallback_basic_report")
            }]

        return falas

    def get_start_dialogue(self, heroes: list, relation_counters: dict = None) -> list:
        if relation_counters is None:
            relation_counters = {}
        
        # Cria set com IDs dos heróis na party
        party_ids = {str(h.id) for h in heroes}
        
        falas = []

        for hero in heroes:
            hero_id = str(hero.id)
            
            # Carrega JSON do herói
            hero_data = self._load_hero_dialogue(hero_id)
            if not hero_data:
                continue
            
            # Navega para diálogos iniciais
            start_data = hero_data.get("start_dialogues", {})
            
            chosen_text = None
            
            # 🎯 PRIORIDADE 1: Verifica cadeias de relação (contador)
            chains = start_data.get("chains", {})


            for other_hero in heroes:
                if other_hero.id == hero.id:
                    continue
                
                # Chave pode ser nome ou ID do outro herói
                other_key = str(other_hero.id)
                
                if other_key not in chains:
                    continue
                
                # Pega o contador de relação
                counter = relation_counters.get(hero_id, {}).get(other_key, 0)
                counter_str = str(counter)
                
                # Verifica se existe texto para esse contador
                lang_block = chains[other_key].get(counter_str, {})
                chain_texts = lang_block.get(self.language)
                if isinstance(chain_texts, list) and chain_texts:
                    chosen_text = random.choice(chain_texts)
                    break  # Encontrou, para de procurar

                print("HERO:", hero_id)
                print("OTHER:", other_key)
                print("COUNTER:", counter_str)
                print("CHAIN EXISTS:", other_key in chains)
                print("LANG BLOCK:", chains.get(other_key, {}).get(counter_str))


            # 🎯 PRIORIDADE 2: Texto base (default)
            if not chosen_text:
                default_block = start_data.get("default", {})
                default_texts = default_block.get(self.language)
                if isinstance(default_texts, list) and default_texts:
                    chosen_text = random.choice(default_texts)
            
            # Adiciona a fala
            if chosen_text:
                falas.append({
                    "id": hero_id,
                    "text": chosen_text
                })
        
        # Fallback
        if not falas:
            return [{
                "id": "assistant",
                "text": self.lm.t("assistant_fallback_silent_start")
            }]
        
        return falas
