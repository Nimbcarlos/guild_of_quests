import json
import random

class DialogueManager:
    def __init__(self, start_path="data/start_dialogues.json", dialogues_path="data/dialogues.json"):
        self.start_dialogues = self._load_dialogues(start_path)
        self.dialogues = self._load_dialogues(dialogues_path)

    def _load_dialogues(self, file_path: str):
        """Carrega os dados de diálogo de um arquivo JSON."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: O arquivo de diálogos '{file_path}' não foi encontrado.")
            return {}
        except json.JSONDecodeError:
            print(f"Erro: O arquivo '{file_path}' tem um formato JSON inválido.")
            return {}

    def get_quest_dialogue(self, quest_id, result):
        result = result.lower()
        dialogue_data = self.dialogues.get(quest_id, {})
        return dialogue_data.get(result)

    def _get_team_key(self, hero_ids: list) -> str:
        """Gera uma chave única para a combinação de heróis."""
        return "_".join(sorted(hero_ids))

    def show_quest_dialogue(self, heroes: list, quest_id: str, result: str):
        """
        Retorna os diálogos como lista de dicionários com 'id' e 'text'.
        Isso permite que o DialogueBox saiba quem está falando.
        """
        quest_id = str(quest_id)
        dialogue_data = self.get_quest_dialogue(quest_id, result)

        if not dialogue_data:
            print("texto com erro", quest_id, result)
            return [{"id": "narrator", "text": "Nenhum diálogo encontrado para esta missão e resultado."}]

        hero_ids = [str(hero.id) for hero in heroes]
        num_heroes = len(hero_ids)

        # 1. PRIORIDADE MÁXIMA: Diálogo específico para esta combinação exata
        team_key = self._get_team_key(hero_ids)
        teams = dialogue_data.get("teams", {})
        
        if team_key in teams:
            # ✅ Retorna os dicionários direto do JSON
            return teams[team_key]

        # 2. SEGUNDA PRIORIDADE: Diálogo genérico para o número de heróis
        multi_key = f"multi_{num_heroes}"
        if multi_key in dialogue_data:
            return dialogue_data[multi_key]

        # 3. TERCEIRA PRIORIDADE: Diálogo genérico para qualquer grupo
        if "multi" in dialogue_data:
            return dialogue_data["multi"]

        # 4. FALLBACK: Diálogos individuais de cada herói
        reporters = dialogue_data.get("reporters", {})
        falas = []
        for hero in heroes:
            hero_id = str(hero.id)
            if hero_id in reporters:
                # ✅ Retorna como dicionário também
                falas.append(reporters[hero_id])
        
        if falas:
            return falas
        
        # 5. ÚLTIMO RECURSO
        return [{"id": "narrator", "text": "A missão está completa. Relatório simples."}]

    def get_start_dialogues(self, hero_id: int, completed_quests):
        if not isinstance(completed_quests, (set, list, tuple)):
            completed_quests = {completed_quests}

        hero_data = self.start_dialogues.get("heroes", {}).get(str(hero_id), {})
        pool = []

        pool.extend(hero_data.get("default", []))

        for key, texts in hero_data.items():
            quest_id = key
            if quest_id in completed_quests:
                pool.extend(texts)

        if not pool:
            return None
        return random.choice(pool)

    def show_start_dialogues(self, heroes: list, completed_quests: set[str]):
        """
        Mostra falas iniciais quando os heróis são enviados.
        Agora retorna dicionários com id e text!
        """
        falas = []
        for hero in heroes:
            fala = self.get_start_dialogues(hero.id, completed_quests)
            if fala:
                # ✅ Retorna como dicionário
                falas.append({
                    "id": str(hero.id),
                    "text": fala
                })
        
        if not falas:
            return [{"id": "narrator", "text": "Os heróis se preparam em silêncio..."}]
        
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