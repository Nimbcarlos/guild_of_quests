import json, random

class DialogueManager:
    def __init__(self, start_path="data/start_dialogues.json", dialogues_path="data/dialogues.json"):
        self.start_dialogues = self._load_dialogues(start_path)
        self.dialogues = self._load_dialogues(dialogues_path)

    def _load_dialogues(self, file_path: str):
        """
        Carrega os dados de diálogo de um arquivo JSON.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Erro: O arquivo de diálogos '{file_path}' não foi encontrado.")
            return {}
        except json.JSONDecodeError:
            print(f"Erro: O arquivo '{file_path}' tem um formato JSON inválido.")
            return {}

    def get_start_dialogues(self, hero_id: int, completed_quests):
        if not isinstance(completed_quests, (set, list, tuple)):
            completed_quests = {completed_quests}  # transforma int em set

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
        """
        falas = []
        for hero in heroes:
            fala = self.get_start_dialogues(hero.id, completed_quests)
            if fala:
                falas.append(f"{hero.name}: {fala}")
        return falas or ["Os heróis se preparam em silêncio..."]

    def get_quest_dialogue(self, quest_id, result):
        # Converte o resultado para minúsculas para corresponder à chave no JSON
        result = result.lower()

        dialogue_data = self.dialogues.get(quest_id, {})
        result_data = dialogue_data.get(result)

        return result_data

    def show_quest_dialogue(self, heroes: list, quest_id: str, result: str):
        quest_id = str(quest_id)
        dialogue_data = self.get_quest_dialogue(quest_id, result)

        if not dialogue_data:
            return ["Nenhum diálogo encontrado para esta missão e resultado."]

        reporters = dialogue_data.get("reporters", {})

        falas = []
        for hero in heroes:
            # Converte o ID do herói para string para corresponder à chave no JSON
            if str(hero.id) in reporters:
                falas.append(reporters[str(hero.id)]["text"])
        if falas:
            return falas
        return ["A missão está completa. Relatório simples."]

# --- Teste ---
if __name__ == '__main__':
    # Uma classe de exemplo para simular o objeto 'hero'
    class DummyHero:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    dm = DialogueManager()

    # Exemplo de chamada com um objeto herói e um resultado com a primeira letra maiúscula
    herois = [DummyHero(id=1, name="Heroi A")]
    teste1 = dm.show_start_dialogues(herois, 2)
    
    for fala in teste1:
        print(fala)
