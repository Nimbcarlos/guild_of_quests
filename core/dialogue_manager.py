import json
import random
import os
from core.language_manager import LanguageManager


class DialogueManager:
    def __init__(self, language="en"):
        self.language = language
        self.lm = LanguageManager()

        # caminhos dinamicos por idioma
        base = f"data/{self.language}"

        self.start_path = os.path.join(base, "start_dialogues.json")
        self.dialogues_path = os.path.join(base, "dialogues.json")

        # fallback se o idioma não existir
        if not os.path.exists(self.start_path):
            print(f"[DialogueManager] Idioma '{self.language}' não encontrado. Usando fallback EN.")
            self.language = "en"
            base = f"data/en"
            self.start_path = os.path.join(base, "start_dialogues.json")
            self.dialogues_path = os.path.join(base, "dialogues.json")

        self.start_dialogues = self._load_dialogues(self.start_path)
        self.dialogues = self._load_dialogues(self.dialogues_path)

    def set_language(self, language):
        """Permite trocar o idioma em tempo real"""
        self.__init__(language)

    def _load_dialogues(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[DialogueManager] Arquivo não encontrado: {file_path}")
            return {}
        except json.JSONDecodeError:
            print(f"[DialogueManager] JSON inválido: {file_path}")
            return {}

    def get_quest_dialogue(self, quest_id, result):
        result = result.lower()
        dialogue_data = self.dialogues.get(str(quest_id), {})
        return dialogue_data.get(result)

    def _get_team_key(self, hero_ids: list) -> str:
        return "_".join(sorted(hero_ids))

    def show_quest_dialogue(self, heroes: list, quest_id: str, result: str):
        quest_id = str(quest_id)
        dialogue_data = self.get_quest_dialogue(quest_id, result)

        if not dialogue_data:
            print("texto com erro", quest_id, result)
            return [{"id": "assistant", "text": self.lm.t("assistant_fallback_no_quest_dialogue")}]

        hero_ids = [str(hero.id) for hero in heroes]
        num_heroes = len(hero_ids)

        # 1 — combinação exata
        team_key = self._get_team_key(hero_ids)
        teams = dialogue_data.get("teams", {})
        
        if team_key in teams:
            return teams[team_key]

        # 2 — genérico por quantidade
        multi_key = f"multi_{num_heroes}"
        if multi_key in dialogue_data:
            return dialogue_data[multi_key]

        # 3 — genérico geral
        if "multi" in dialogue_data:
            return dialogue_data["multi"]

        # 4 — fallback individual
        reporters = dialogue_data.get("reporters", {})
        falas = []
        for hero in heroes:
            hero_id = str(hero.id)
            if hero_id in reporters:
                falas.append(reporters[hero_id])
        
        if falas:
            return falas
        
        return [{"id": "assistant", "text": self.lm.t("assistant_fallback_basic_report")}]

    def get_start_dialogues(self, hero_id: int, completed_quests):
        if not isinstance(completed_quests, (set, list, tuple)):
            completed_quests = {completed_quests}

        hero_data = self.start_dialogues.get("heroes", {}).get(str(hero_id), {})
        pool = []

        pool.extend(hero_data.get("default", []))

        for key, texts in hero_data.items():
            if key in completed_quests:
                pool.extend(texts)

        if not pool:
            return None
        return random.choice(pool)

    def show_start_dialogues(self, heroes: list, completed_quests: set[str]):
        falas = []
        for hero in heroes:
            fala = self.get_start_dialogues(hero.id, completed_quests)
            if fala:
                falas.append({
                    "id": str(hero.id),
                    "text": fala
                })
        
        if not falas:
            return [{"id": "assistant", "text": self.lm.t("assistant_fallback_silent_start")}]
        
        return falas


# --- Teste ---
if __name__ == '__main__':
    class DummyHero:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    dm = DialogueManager()

    herois = [DummyHero(id=2, name="Elara"), DummyHero(id=3, name="Kael")]
    teste1 = dm.show_quest_dialogue(herois, "1", "sucesso")
    
    print("=== TESTE: Diálogos retornados ===")
    for i, fala in enumerate(teste1):
        print(f"{i}: {fala}")