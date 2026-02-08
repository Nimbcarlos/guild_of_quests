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


    def _load_quest_dialogue(self, quest_id: str) -> dict:
        path = os.path.join("data/quests", f"{quest_id}.json")

        if not os.path.exists(path):
            print(f"[DialogueManager] Quest dialogue não encontrado: {path}")
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[DialogueManager] Erro ao carregar quest {quest_id}: {e}")
            return {}

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

    def show_quest_dialogue(
        self,
        heroes: list,
        quest_id: str,
        result: str,
        quest_type: str = None,
        context: dict | None = None
    ) -> list:

        quest_id = str(quest_id)
        result = result.lower()

        if context is None:
            context = {}

        ROLE_ORDER = {
            "tank": 0,
            "dps": 1,
            "healer": 2
        }

        # ───────────────────────────────────────────
        # Ordena heróis por papel narrativo
        # ───────────────────────────────────────────
        ordered_heroes = sorted(
            heroes,
            key=lambda h: ROLE_ORDER.get((h.role or "").lower(), 99)
        )

        if not ordered_heroes:
            return [{
                "id": "assistant",
                "text": self.lm.t("assistant_fallback_basic_report")
            }]

        # ───────────────────────────────────────────
        # 🎯 Define herói âncora
        # ───────────────────────────────────────────
        anchor_hero = None
        for role in ("tank", "dps", "healer"):
            for h in ordered_heroes:
                if (h.role or "").lower() == role:
                    anchor_hero = h
                    break
            if anchor_hero:
                break

        if not anchor_hero:
            anchor_hero = min(ordered_heroes, key=lambda h: int(h.id))

        anchor_id = str(anchor_hero.id)
        party_key = "alone" if len(ordered_heroes) == 1 else "group"

        # ───────────────────────────────────────────
        # Carrega diálogo da quest (conclusão)
        # ───────────────────────────────────────────
        quest_dialogue = self._load_quest_dialogue(quest_id)

        falas = []

        # ───────────────────────────────────────────
        # Montagem das falas
        # ───────────────────────────────────────────
        for index, hero in enumerate(ordered_heroes):
            hero_id = str(hero.id)

            hero_data = self._load_hero_dialogue(hero_id)
            if not hero_data:
                continue

            fight_blocks = hero_data.get("fight_blocks")

            parts = []

            # ───────── ARRIVED ─────────
            if hero_id == anchor_id and fight_blocks:
                arrived_texts = (
                    fight_blocks
                    .get("arrived", {})
                    .get(party_key, {})
                    .get(self.language)
                )

                if isinstance(arrived_texts, list) and arrived_texts:
                    text = random.choice(arrived_texts)
                    parts.append(text.format(**context))

            # ───────── ACTION ─────────
            if fight_blocks:
                action_texts = (
                    fight_blocks
                    .get("action", {})
                    .get(party_key, {})
                    .get(self.language)
                )

                if isinstance(action_texts, list) and action_texts:
                    text = random.choice(action_texts)
                    parts.append(text.format(**context))

            # ───────── OTHERS ─────────
            if fight_blocks and len(ordered_heroes) > 1:
                others_block = fight_blocks.get("others", {})

                for other in ordered_heroes:
                    if other.id == hero.id:
                        continue

                    other_id = str(other.id)
                    other_texts = (
                        others_block
                        .get(other_id, {})
                        .get(party_key, {})
                        .get(self.language)
                    )

                    if isinstance(other_texts, list) and other_texts:
                        text = random.choice(other_texts)
                        text = text.replace(
                            "{hero_name}",
                            getattr(other, "name", f"hero_{other_id}")
                        )
                        parts.append(text.format(**context))
                        break

            # ───────── CONCLUSION ─────────
            is_last = index == len(ordered_heroes) - 1
            if is_last:
                conclusion_texts = (
                    quest_dialogue
                    .get("conclusion", {})
                    .get(result, {})
                    .get(self.language)
                )

                if isinstance(conclusion_texts, list) and conclusion_texts:
                    text = random.choice(conclusion_texts)
                    parts.append(text.format(**context))

            # ───────── FINAL ─────────
            if parts:
                final_text = " ".join(parts)
                falas.append({
                    "id": hero_id,
                    "text": final_text
                })

        # ───────────────────────────────────────────
        # Fallback final
        # ───────────────────────────────────────────
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


if __name__ == "__main__":
    dm = DialogueManager(language="en")
    

    dialogues = dm.show_quest_dialogue(1, quest_id=0, result="success")
    for fala in dialogues:
        print(f"{fala['id']}: {fala['text']}")