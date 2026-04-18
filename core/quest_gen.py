import json
import random
from pathlib import Path
from typing import Dict, List, Literal, Optional, TypedDict

from core.quest import Quest
from core.map_graph import MapGraph

QuestType = Literal[
    "fight",
    "diplomacy",
    "nature",
    "athletics",
    "thievery",
    "religion",
    "arcana",
    "intimidation",
    "survival",
    "cure",
    "performance",
    "investigation",
    "alchemy",
    "stealth",
]


class QuestData(TypedDict, total=False):
    seed: int
    id: int
    name: Dict[str, str]
    description: Dict[str, str]
    type: str
    max_heroes: int
    expired_at: int
    available_from_turn: int
    duration: int
    difficulty: int
    rewards: Dict[str, int]
    required_quests: List[int]
    forbidden_quests: List[int]
    required_perks: List[str]
    context: Dict[str, str]
    conclusion: Dict[str, Dict[str, str]]
    is_procedural: bool


class ProceduralQuestSystem:

    SUPPORTED_LANGUAGES = {"pt", "en", "es", "zh", "ja", "ru"}

    def __init__(self, language: str = "pt", data_file: str = "data/quest_data.json"):
        self.language = language if language in self.SUPPORTED_LANGUAGES else "pt"
        self.data_file = Path(data_file)

        self.actions: Dict = {}
        self.subjects: Dict = {}
        self.locations: Dict = {}
        self.sub_locations: Dict = {}
        self.modifiers: Dict = {}
        self.incompatible_modes: Dict = {}
        self.text_fragments: Dict = {}
        self.action_subject_rules: Dict = {}
        self.modifier_subject_rules: Dict = {}
        self.modifier_chance_by_action: Dict = {}
        self.max_heroes_weights: Dict = {}

        self.location_groups_raw: Dict = {}
        self.sub_location_groups_raw: Dict = {}

        self.type_by_id: Dict = {}
        self.verb_by_type_and_id: Dict = {}
        self.subject_by_id: Dict = {}
        self.location_by_id: Dict = {}
        self.sub_location_by_id: Dict = {}
        self.modifier_by_id: Dict = {}

        self.seeds = {
            "available": set(),
            "active": {},
            "completed": set(),
        }

        self._load_data()
        self._build_indexes()


    # ============================================================
    # LOAD / INDEX
    # ============================================================

    def _load_data(self) -> None:
        try:
            with self.data_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            self.actions = data.get("actions", {})
            self.subjects = data.get("subjects", {})
            self.modifiers = data.get("modifiers", {})
            self.incompatible_modes = data.get("incompatible_modes", {})
            self.text_fragments = data.get("text_fragments", {})
            self.action_subject_rules = data.get("action_subject_rules", {})
            self.modifier_subject_rules = data.get("modifier_subject_rules", {})
            self.modifier_chance_by_action = data.get("modifier_chance_by_action", {})
            self.max_heroes_weights = data.get("max_heroes_weights", {})

            self.location_groups_raw = data.get("locations", {})
            self.sub_location_groups_raw = data.get("sub_locations", {})

            self.locations = self._flatten_grouped_entries(self.location_groups_raw, mode="location")
            self.sub_locations = self._flatten_grouped_entries(self.sub_location_groups_raw, mode="sub_location")

            self._validate_loaded_data()

            bridges_data = {}
            
            if "sub_locations" in data:
                # Procura grupo "bridge"
                bridge_group = data["sub_locations"].get("bridge", {})
                
                for bridge_key, bridge_data in bridge_group.items():
                    # Só pontes (ignora "context" e outras coisas)
                    if isinstance(bridge_data, dict) and "locations" in bridge_data:
                        bridges_data[bridge_key] = bridge_data
            
            # ✅ CONSTRÓI MAPA AUTOMATICAMENTE
            self.map_graph = MapGraph(bridges_data)
            
            print(f"🗺️  Mapa construído: {len(self.map_graph.graph)} locations")
            print(f"🌉 {len(bridges_data)} pontes encontradas")

        except FileNotFoundError:
            print(f"[ProcSystem] ❌ Arquivo não encontrado: {self.data_file}")
            self._create_default_data()
        except json.JSONDecodeError as e:
            print(f"[ProcSystem] ❌ Erro ao ler JSON: {e}")
            raise
        except ValueError as e:
            print(f"[ProcSystem] ❌ Dados inválidos: {e}")
            raise

    def _create_default_data(self) -> None:
        self.actions = {}
        self.subjects = {}
        self.locations = {}
        self.sub_locations = {}
        self.modifiers = {}
        self.incompatible_modes = {}
        self.text_fragments = {}
        self.action_subject_rules = {}
        self.modifier_subject_rules = {}
        self.modifier_chance_by_action = {}
        self.max_heroes_weights = {}
        self.location_groups_raw = {}
        self.sub_location_groups_raw = {}
        self.type_by_id = {}
        self.verb_by_type_and_id = {}
        self.subject_by_id = {}
        self.location_by_id = {}
        self.sub_location_by_id = {}
        self.modifier_by_id = {}

    def _flatten_grouped_entries(self, raw_groups: Dict, mode: str) -> Dict:
        flat: Dict = {}

        for group_key, children in raw_groups.items():
            if not isinstance(children, dict):
                raise ValueError(f"Grupo '{group_key}' deve conter um objeto")

            for child_key, child_data in children.items():
                if not isinstance(child_data, dict):
                    raise ValueError(f"Entrada '{child_key}' dentro de '{group_key}' deve ser um objeto")

                item = dict(child_data)
                item["key"] = child_key

                if mode == "location":
                    item.setdefault("group", group_key)
                elif mode == "sub_location":
                    item.setdefault("type", group_key)
                else:
                    raise ValueError(f"Modo inválido em _flatten_grouped_entries: {mode}")

                flat[child_key] = item

        return flat

    def _validate_loaded_data(self) -> None:
        if not self.actions:
            raise ValueError("JSON sem 'actions'")
        if not self.subjects:
            raise ValueError("JSON sem 'subjects'")
        if not self.locations:
            raise ValueError("JSON sem 'locations'")
        if not self.sub_locations:
            raise ValueError("JSON sem 'sub_locations'")
        if not self.modifiers:
            raise ValueError("JSON sem 'modifiers'")

        for action_key, categories in self.action_subject_rules.items():
            if action_key not in self.actions:
                raise ValueError(f"Regra de action_subject_rules para action inexistente: '{action_key}'")
            if not isinstance(categories, list) or not categories:
                raise ValueError(f"action_subject_rules['{action_key}'] deve ser uma lista não vazia")

        for action_key, action_data in self.actions.items():
            if "id" not in action_data:
                raise ValueError(f"Action '{action_key}' sem 'id'")
            if "verbs" not in action_data or not action_data["verbs"]:
                raise ValueError(f"Action '{action_key}' sem verbos")

        for subject_key, subject_data in self.subjects.items():
            sub_location_groups = subject_data.get("locations", [])
            if not isinstance(sub_location_groups, list):
                raise ValueError(f"Subject '{subject_key}' com locations inválido")

            for sub_location_group_key in sub_location_groups:
                if sub_location_group_key not in self.sub_location_groups_raw:
                    raise ValueError(
                        f"Subject '{subject_key}' referencia grupo de sub_location inexistente: '{sub_location_group_key}'"
                    )

        for sub_location_group_key, sub_location_group in self.sub_location_groups_raw.items():
            if not isinstance(sub_location_group, dict) or not sub_location_group:
                raise ValueError(f"Grupo de sub_locations '{sub_location_group_key}' inválido ou vazio")

            for sub_location_key, sub_location_data in sub_location_group.items():
                location_keys = sub_location_data.get("locations", [])
                if not isinstance(location_keys, list) or not location_keys:
                    raise ValueError(
                        f"Sub-location '{sub_location_key}' sem lista 'locations' válida"
                    )

                for location_key in location_keys:
                    if location_key not in self.locations:
                        raise ValueError(
                            f"Sub-location '{sub_location_key}' referencia location inexistente: '{location_key}'"
                        )

    def _build_indexes(self) -> None:
        self.type_by_id = {
            data["id"]: action_key
            for action_key, data in self.actions.items()
        }

        self.verb_by_type_and_id = {}
        for action_key, action_data in self.actions.items():
            self.verb_by_type_and_id[action_key] = {
                verb_data["id"]: verb_data
                for _, verb_data in action_data.get("verbs", {}).items()
            }

        self.subject_by_id = {
            data["id"]: data
            for _, data in self.subjects.items()
        }

        self.location_by_id = {
            data["id"]: data
            for _, data in self.locations.items()
        }

        self.sub_location_by_id = {
            data["id"]: data
            for _, data in self.sub_locations.items()
        }

        self.modifier_by_id = {
            data["id"]: data
            for _, data in self.modifiers.items()
        }

    # ============================================================
    # RANDOM / LOOKUP
    # ============================================================

    def _random_key(self, mapping: Dict) -> str:
        if not mapping:
            raise ValueError("Map vazio para escolha aleatória")
        return random.choice(list(mapping.keys()))

    def _get_action(self, quest_type: str) -> Dict:
        action = self.actions.get(quest_type)
        if not action:
            raise ValueError(f"Tipo '{quest_type}' não existe no JSON")
        return action

    def _get_verb_data(self, quest_type: str, verb_key: Optional[str] = None) -> Dict:
        action = self._get_action(quest_type)
        verbs = action.get("verbs", {})
        if not verbs:
            raise ValueError(f"Tipo '{quest_type}' não possui verbos")

        if verb_key is None:
            verb_key = self._random_key(verbs)

        verb = verbs.get(verb_key)
        if not verb:
            raise ValueError(f"Verbo '{verb_key}' não existe em '{quest_type}'")
        return verb

    def _get_type_by_id(self, type_id: int) -> str:
        try:
            return self.type_by_id[type_id]
        except KeyError:
            raise ValueError(f"Tipo ID {type_id} não encontrado")

    def _get_verb_by_id(self, quest_type: str, verb_id: int) -> Dict:
        try:
            return self.verb_by_type_and_id[quest_type][verb_id]
        except KeyError:
            raise ValueError(f"Verbo ID {verb_id} não encontrado em '{quest_type}'")

    def _get_subject_by_id(self, subject_id: int) -> Dict:
        try:
            return self.subject_by_id[subject_id]
        except KeyError:
            raise ValueError(f"Subject ID {subject_id} não encontrado")

    def _get_location_by_id(self, location_id: int) -> Dict:
        try:
            return self.location_by_id[location_id]
        except KeyError:
            raise ValueError(f"Location ID {location_id} não encontrado")

    def _get_sub_location_by_id(self, sub_location_id: int) -> Dict:
        try:
            return self.sub_location_by_id[sub_location_id]
        except KeyError:
            raise ValueError(f"Sub-location ID {sub_location_id} não encontrado")

    def _get_modifier_by_id(self, modifier_id: int) -> Dict:
        try:
            return self.modifier_by_id[modifier_id]
        except KeyError:
            raise ValueError(f"Modifier ID {modifier_id} não encontrado")

    # ============================================================
    # SEED
    # ============================================================

    def generate_seed(
        self,
        quest_type: str,
        party_level: int = 1,
        verb_key: Optional[str] = None,
        subject_key: Optional[str] = None,
        location_key: Optional[str] = None,
        sub_location_key: Optional[str] = None,
        modifier_key: Optional[str] = None,
        max_heroes: Optional[int] = None,
        expired_at: Optional[int] = None,
        duration: Optional[int] = None,
    ) -> int:
        action = self._get_action(quest_type)
        verb = self._get_verb_data(quest_type, verb_key)
        subject = self._get_subject_data_for_action(quest_type, party_level, subject_key)
        sub_location = self._get_sub_location_for_subject(subject, sub_location_key)
        location = self._get_location_for_sub_location(sub_location, location_key)
        modifier = self._get_modifier_for_subject(subject, modifier_key, quest_type)

        max_heroes = self._get_max_heroes(max_heroes)
        expired_at = self._clamp(expired_at if expired_at is not None else random.randint(3, 7), 1, 9)
        duration = self._clamp(duration if duration is not None else random.randint(2, 5), 1, 9)

        seed_str = (
            f"{action['id']:02d}"
            f"{verb['id']:02d}"
            f"{subject['id']:02d}"
            f"{location['id']:02d}"
            f"{sub_location.get('id', 0):02d}"
            f"{modifier['id']:02d}"
            f"{max_heroes:01d}"
            f"{expired_at:01d}"
            f"{duration:01d}"
        )
        return int(seed_str)

    def decode_seed(self, seed: int) -> Dict[str, int]:
        seed_str = str(seed).zfill(15)
        return {
            "type_id": int(seed_str[0:2]),
            "verb_id": int(seed_str[2:4]),
            "subject_id": int(seed_str[4:6]),
            "location_id": int(seed_str[6:8]),
            "sub_location_id": int(seed_str[8:10]),
            "modifier_id": int(seed_str[10:12]),
            "max_heroes": int(seed_str[12:13]),
            "expired_at": int(seed_str[13:14]),
            "duration": int(seed_str[14:15]),
        }

    # ============================================================
    # QUEST BUILD
    # ============================================================

    def reconstruct_quest_from_seed(self, seed: int) -> QuestData:
        parts = self.decode_seed(seed)

        quest_type = self._get_type_by_id(parts["type_id"])
        verb = self._get_verb_by_id(quest_type, parts["verb_id"])
        subject = self._get_subject_by_id(parts["subject_id"])
        location = self._get_location_by_id(parts["location_id"])

        sub_location_id = parts.get("sub_location_id", 0)
        if sub_location_id > 0:
            sub_location = self._get_sub_location_by_id(sub_location_id)
        else:
            sub_location = {"id": 0, "pt": "", "en": "", "es": "", "ru": "", "zh": "", "ja": ""}

        modifier = self._get_modifier_by_id(parts["modifier_id"])

        difficulty_value = (
            verb.get("difficulty", 1.0)
            * subject.get("power", 1.0)
            * location.get("danger", 1.0)
            + sub_location.get("danger_add", 0.0)
            + modifier.get("difficulty_add", 0.0)
        )

        heroes_multiplier = {1: 1.00, 2: 1.35, 3: 1.70, 4: 2.05}.get(parts["max_heroes"], 1.0)
        duration_multiplier = {1: 1.00, 2: 1.08, 3: 1.15, 4: 1.22, 5: 1.28}.get(parts["duration"], 1.30)
        xp = int((difficulty_value * 45) * heroes_multiplier * duration_multiplier)

        description = self._generate_description(quest_type, verb, subject, location, sub_location, modifier)
        conclusion = self._generate_conclusion(quest_type, subject, location, sub_location, modifier)
        narrative_context = self._generate_context(subject, location, sub_location, modifier)

        context = {
            "location": self._compose_location_phrase(sub_location, location, self.language),
            "location_key": location.get("key", ""),
            "sub_location_key": sub_location.get("key", ""),
            "location_type": sub_location.get("type", ""),   # ← "bridge", "forest", etc
            "enemy": self._compose_subject_phrase(quest_type, subject, modifier, self.language),
            "enemy_type": self._get_modifier_form(modifier, subject, self.language),
            "subject_category": subject.get("category", "unknown"),
            "action_type": quest_type,
            "narrative": narrative_context[self.language],
        }

        sub_loc_text_pt = self._get_location_with_preposition(sub_location, "em", "pt")
        sub_loc_text_en = self._get_location_with_preposition(sub_location, "em", "en")
        sub_loc_text_es = self._get_location_with_preposition(sub_location, "em", "es")

        return {
            "seed": seed,
            "id": seed,
            "name": {
                "pt": f"{verb.get('pt', '')} {self._compose_subject_phrase(quest_type, subject, modifier, 'pt')} {sub_loc_text_pt}".strip(),
                "en": f"{verb.get('en', '')} {self._compose_subject_phrase(quest_type, subject, modifier, 'en')} {sub_loc_text_en}".strip(),
                "es": f"{verb.get('es', verb.get('en', ''))} {self._compose_subject_phrase(quest_type, subject, modifier, 'es')} {sub_loc_text_es}".strip(),
                "ru": f"{verb.get('ru', '')} {self._compose_subject_phrase(quest_type, subject, modifier, 'ru')}",
                "zh": f"{verb.get('zh', '')} {self._compose_subject_phrase(quest_type, subject, modifier, 'zh')}",
                "ja": f"{verb.get('ja', '')} {self._compose_subject_phrase(quest_type, subject, modifier, 'ja')}",
            },
            "description": description,
            "type": quest_type,
            "max_heroes": parts["max_heroes"],
            "expired_at": parts["expired_at"],
            "available_from_turn": 1,
            "duration": parts["duration"],
            "difficulty": max(1, round(difficulty_value)),
            "rewards": {"xp": xp},
            "required_quests": [],
            "forbidden_quests": [],
            "required_perks": [],
            "context": context,
            "conclusion": conclusion,
            "is_procedural": True,
        }

    def to_quest_object(self, quest_data: QuestData) -> Quest:
        quest = Quest(
            id=quest_data["id"],
            name=quest_data["name"],
            description=quest_data["description"],
            type=quest_data["type"],
            max_heroes=quest_data["max_heroes"],
            expired_at=quest_data.get("expired_at", 5),
            available_from_turn=quest_data.get("available_from_turn", 1),
            duration=quest_data["duration"],
            difficulty=quest_data["difficulty"],
            rewards=quest_data["rewards"],
            required_quests=quest_data.get("required_quests", []),
            forbidden_quests=quest_data.get("forbidden_quests", []),
            required_perks=quest_data.get("required_perks", []),
            context=quest_data.get("context", {}),
            conclusion=quest_data.get("conclusion", {}),
            language=self.language,
        )

        quest.is_procedural = True
        quest.seed = quest_data["seed"]
        return quest

    # ============================================================
    # PUBLIC API
    # ============================================================

    def generate_quest_of_type(self, quest_type: QuestType, party_level: int = 1) -> Quest:
        seed = self.generate_seed(quest_type, party_level)
        quest_data = self.reconstruct_quest_from_seed(seed)
        return self.to_quest_object(quest_data)

    def get_quest_from_seed(self, seed: int) -> Quest:
        quest_data = self.reconstruct_quest_from_seed(seed)
        return self.to_quest_object(quest_data)

    def ensure_min_available(self, min_count: int = 3) -> List[Quest]:
        all_types = list(self.actions.keys())
        if not all_types:
            return []

        while len(self.seeds["available"]) < min_count:
            used_seeds = self.seeds["available"] | set(self.seeds["active"].keys()) | self.seeds["completed"]
            seed = None

            for _ in range(100):
                quest_type = random.choice(all_types)
                candidate = self.generate_seed(quest_type)
                if candidate not in used_seeds:
                    seed = candidate
                    break

            if seed is None:
                break

            self.seeds["available"].add(seed)

        return self.get_available_quests()

    def get_available_quests(self) -> List[Quest]:
        return [self.get_quest_from_seed(seed) for seed in self.seeds["available"]]

    def mark_as_active(self, seed: int, heroes: Optional[List[int]] = None, turns_left: int = 1) -> None:
        if seed in self.seeds["available"]:
            self.seeds["available"].remove(seed)

        self.seeds["active"][seed] = {
            "turns_left": max(1, turns_left),
            "heroes": heroes or [],
        }

    def complete_quest(self, seed: int) -> None:
        self.seeds["active"].pop(seed, None)
        self.seeds["available"].discard(seed)
        self.seeds["completed"].add(seed)

    # ============================================================
    # TEXT HELPERS
    # ============================================================

    def _generate_description(self, quest_type: str, verb: dict, subject: dict, location: dict, sub_location: dict, modifier: dict) -> dict:
        fragments_root = self.text_fragments.get("description", {})
        type_fragments = fragments_root.get(quest_type, {})
        result = {}

        for lang in self.SUPPORTED_LANGUAGES:
            intro_tpl = self._pick_fragment(type_fragments, "intro", lang, required=False)
            context_tpl = self._pick_fragment(type_fragments, "objective_context", lang, required=False)
            objective_tpl = self._pick_fragment(type_fragments, "objective", lang, required=False)
            detail_tpl = self._pick_fragment(type_fragments, "detail", lang, required=False)
            pressure_tpl = self._pick_fragment(type_fragments, "pressure", lang, required=False)

            subject_phrase = self._compose_subject_phrase(quest_type, subject, modifier, lang)
            sub = self._get_location_with_preposition(sub_location, "de", lang)
            loc = self._get_location_with_preposition(location, "em", lang)

            location_text = f"{sub} {loc}"

            text_parts = []
            if intro_tpl:
                text_parts.append(intro_tpl.strip())
            if objective_tpl:
                if context_tpl:
                    phrase = f"{objective_tpl.strip()} {subject_phrase} {context_tpl} {location_text}."
                else:
                    phrase = f"{objective_tpl.strip()} {subject_phrase} {location_text}."
                
                text_parts.append(phrase.strip())
            if detail_tpl:
                text_parts.append(
                    detail_tpl.format(
                        verb=self._localize(verb, lang),
                        subject=self._get_subject_text(subject, lang),
                        modifier=self._get_modifier_form(modifier, subject, lang),
                        subject_phrase=subject_phrase,
                        location=location_text,
                    ).strip()
                )
            if pressure_tpl:
                text_parts.append(pressure_tpl.strip())

            result[lang] = " ".join(part for part in text_parts if part).strip()

        return result

    def _generate_conclusion(self, quest_type: str, subject: Dict, location: Dict, sub_location: Dict, modifier: Dict) -> Dict[str, Dict[str, str]]:
        pt_subject = self._get_subject_text(subject, "pt") or "alvos"
        en_subject = self._get_subject_text(subject, "en") or "targets"
        es_subject = self._get_subject_text(subject, "es") or en_subject

        pt_modifier = self._get_modifier_form(modifier, subject, "pt")
        en_modifier = self._get_modifier_form(modifier, subject, "en")
        es_modifier = self._get_modifier_form(modifier, subject, "es") or en_modifier

        pt_location = self._compose_location_phrase(location, sub_location, "pt") or "na região"
        en_location = self._compose_location_phrase(location, sub_location, "en") or "in the region"
        es_location = self._compose_location_phrase(location, sub_location, "es") or en_location

        return {
            "success": {
                "pt": f"A operação contra {pt_subject} {pt_modifier} {pt_location} foi concluída com sucesso.".strip(),
                "en": f"The operation against the {en_modifier} {en_subject} {en_location} was completed successfully.".strip(),
                "es": f"La operación contra {es_subject} {es_modifier} {es_location} fue completada con éxito.".strip(),
            },
            "failure": {
                "pt": f"A missão envolvendo {pt_subject} {pt_modifier} {pt_location} falhou.".strip(),
                "en": f"The mission involving the {en_modifier} {en_subject} {en_location} has failed.".strip(),
                "es": f"La misión relacionada con {es_subject} {es_modifier} {es_location} ha fracasado.".strip(),
            },
        }

    def _localize(self, data: dict, lang: str) -> str:
        value = data.get(lang) or data.get("pt") or data.get("en") or ""
        if isinstance(value, dict):
            return value.get("text", "")
        return value

    def _pick_fragment(self, fragments: dict, group: str, lang: str, required: bool = True) -> str:
        options = fragments.get(group, [])
        if not options:
            return ""
        chosen = random.choice(options)
        return chosen.get(lang) or chosen.get("pt") or chosen.get("en") or ""

    def _compose_subject_phrase(self, quest_type: str, subject: dict, modifier: dict, lang: str) -> str:
        subject_text = self._get_subject_text(subject, lang)
        modifier_text = self._get_modifier_form(modifier, subject, lang)

        action = self.actions.get(quest_type, {})
        use_article = action.get("use_indefinite_article", False)
        grammar = self._get_subject_grammar(subject, lang)
        number = grammar.get("number", "singular")

        forms = modifier.get("forms", {}).get(lang, {})
        placement = "after"
        if "default_before" in forms:
            placement = "before"
        elif "default_after" in forms:
            placement = "after"
        elif lang == "en":
            placement = "before"

        if modifier_text:
            if placement == "before":
                core = f"{modifier_text}{subject_text}".strip() if lang in {"zh", "ja"} else f"{modifier_text} {subject_text}".strip()
            else:
                core = f"{subject_text} {modifier_text}".strip()
        else:
            core = subject_text

        if use_article and number == "singular":
            article = self._get_indefinite_article(subject, lang)
            if article and lang not in {"zh", "ja"}:
                return f"{article} {core}".strip()

        return core

    def _get_subject_grammar(self, subject: dict, lang: str) -> dict:
        value = subject.get(lang, {})
        return value if isinstance(value, dict) else {}

    def _get_subject_text(self, subject: dict, lang: str) -> str:
        subject_data = subject.get(lang) or subject.get("pt") or subject.get("en")
        if isinstance(subject_data, str):
            return subject_data
        if isinstance(subject_data, dict):
            return subject_data.get("text", "")
        return ""

    def _get_indefinite_article(self, subject: dict, lang: str) -> str:
        grammar = self._get_subject_grammar(subject, lang)
        return grammar.get("article_indefinite", "")

    def _get_modifier_form(self, modifier: dict, subject: dict, lang: str) -> str:
        forms = modifier.get("forms", {})
        lang_forms = forms.get(lang, {})

        if lang in {"pt", "es"}:
            grammar = self._get_subject_grammar(subject, lang)
            gender = grammar.get("gender", "m")
            number = grammar.get("number", "singular")
            key = f"{gender}_{number}"
            return lang_forms.get(key, "")

        if "default_before" in lang_forms:
            return lang_forms["default_before"]
        if "default_after" in lang_forms:
            return lang_forms["default_after"]
        return ""

    def _compose_location_phrase(self, location: dict, sub_location: dict, lang: str) -> str:
        loc_text = self._localize(location, lang)
        sub_text = self._localize(sub_location, lang)

        if not sub_text:
            return loc_text
        if not loc_text:
            return sub_text

        if lang == "pt":
            return f"{sub_text} {loc_text.replace('nos ', 'dos ').replace('no ', 'do ').replace('na ', 'da ').replace('nas ', 'das ')}"
        return f"{sub_text} {loc_text}"

    # ============================================================
    # VALIDATION / SELECTION
    # ============================================================

    def _is_valid_subject_for_action(self, quest_type: str, subject: Dict) -> bool:
        allowed_categories = self.action_subject_rules.get(quest_type)
        if not allowed_categories:
            return True

        subject_category = subject.get("category")
        if not subject_category:
            return False

        return subject_category in allowed_categories

    def _get_subject_data_for_action(self, quest_type: str, party_level: int, subject_key: Optional[str] = None) -> Dict:
        if subject_key is not None:
            subject = self.subjects.get(subject_key)
            if not subject:
                raise ValueError(f"Subject '{subject_key}' não existe")
            if not self._is_valid_subject_for_action(quest_type, subject):
                raise ValueError(f"Subject '{subject_key}' incompatível com '{quest_type}'")

            subject_copy = dict(subject)
            subject_copy["key"] = subject_key
            return subject_copy

        candidates = []
        for key, subject in self.subjects.items():
            if not self._is_valid_subject_for_action(quest_type, subject):
                continue

            min_level = subject.get("min_level", 1)
            max_level = subject.get("max_level", 99)
            if party_level < min_level:
                continue

            weight = subject.get("weight", 10)
            if party_level > max_level:
                weight = max(1, weight // 4)

            subject_copy = dict(subject)
            subject_copy["key"] = key
            candidates.append((subject_copy, weight))

        if not candidates:
            raise ValueError(f"Nenhum subject válido para '{quest_type}' no nível {party_level}")

        return self._weighted_choice(candidates)

    def _get_sub_location_for_subject(self, subject: Dict, sub_location_key: Optional[str] = None) -> Dict:
        subject_key = subject.get("key", "?")
        sub_location_group_keys = subject.get("locations", [])

        if not sub_location_group_keys:
            raise ValueError(f"Subject '{subject_key}' sem grupos de sub_location definidos")

        valid_sub_locations = []
        for group_key in sub_location_group_keys:
            sub_location_group = self.sub_location_groups_raw.get(group_key, {})
            for key, sub_location_data in sub_location_group.items():
                sub_location = dict(sub_location_data)
                sub_location["key"] = key
                sub_location["type"] = group_key
                valid_sub_locations.append(sub_location)

        unique_sub_locations = {}
        for sub_location in valid_sub_locations:
            unique_sub_locations[sub_location["key"]] = sub_location
        valid_sub_locations = list(unique_sub_locations.values())

        if not valid_sub_locations:
            raise ValueError(f"Subject '{subject_key}' não possui sub_locations válidas")

        if sub_location_key is not None:
            for sub_location in valid_sub_locations:
                if sub_location["key"] == sub_location_key:
                    return sub_location
            raise ValueError(f"Sub-location '{sub_location_key}' inválida para subject '{subject_key}'")

        weighted_sub_locations = [(sub_location, sub_location.get("weight", 10)) for sub_location in valid_sub_locations]
        return self._weighted_choice(weighted_sub_locations)

    def _get_location_for_sub_location(self, sub_location: Dict, location_key: Optional[str] = None) -> Dict:
        valid_keys = sub_location.get("locations", [])

        if not valid_keys:
            raise ValueError(f"Sub-location '{sub_location.get('key', '')}' sem locations definidas")

        if location_key is not None:
            if location_key not in valid_keys:
                raise ValueError(
                    f"Location '{location_key}' incompatível com sub-location '{sub_location.get('key', '')}'"
                )
            chosen_key = location_key
        else:
            chosen_key = random.choice(valid_keys)

        location = dict(self.locations[chosen_key])
        location["key"] = chosen_key
        return location

    def _is_valid_modifier_for_subject(self, modifier: Dict, subject: Dict) -> bool:
        modifier_key = modifier.get("key")
        if not modifier_key:
            return True

        allowed_categories = self.modifier_subject_rules.get(modifier_key)
        if not allowed_categories:
            return True

        subject_category = subject.get("category")
        return subject_category in allowed_categories

    def _get_modifier_for_subject(self, subject: Dict, modifier_key: Optional[str] = None, quest_type: Optional[str] = None) -> Dict:
        if modifier_key:
            modifier = dict(self.modifiers.get(modifier_key, {}))
            if not modifier:
                raise ValueError(f"Modifier '{modifier_key}' não existe")
            modifier["key"] = modifier_key

            if not self._is_valid_modifier_for_subject(modifier, subject):
                raise ValueError(
                    f"Modifier '{modifier_key}' é incompatível com subject category='{subject.get('category')}'"
                )
            return modifier

        action_rules = self.modifier_chance_by_action.get(quest_type or "", {})
        none_weight = action_rules.get("none", 80)
        special_weight = action_rules.get("special", 20)
        roll_total = none_weight + special_weight
        roll = random.uniform(0, roll_total)

        if roll <= none_weight:
            modifier = dict(self.modifiers["none"])
            modifier["key"] = "none"
            return modifier

        valid_modifiers = []
        for key, mod in self.modifiers.items():
            if key == "none":
                continue
            mod_copy = dict(mod)
            mod_copy["key"] = key
            if self._is_valid_modifier_for_subject(mod_copy, subject):
                valid_modifiers.append((mod_copy, mod_copy.get("weight", 10)))

        if not valid_modifiers:
            modifier = dict(self.modifiers["none"])
            modifier["key"] = "none"
            return modifier

        return self._weighted_choice(valid_modifiers)

    # ============================================================
    # UTILS
    # ============================================================

    @staticmethod
    def _clamp(value: int, min_value: int, max_value: int) -> int:
        return max(min_value, min(max_value, value))

    def _weighted_choice(self, items: list[tuple[dict, int]]) -> dict:
        total = sum(weight for _, weight in items)
        roll = random.uniform(0, total)
        current = 0

        for item, weight in items:
            current += weight
            if roll <= current:
                return item

        return items[-1][0]

    def _weighted_choice_simple(self, choices: list[tuple[object, int]]):
        total = sum(weight for _, weight in choices)
        roll = random.uniform(0, total)
        current = 0

        for value, weight in choices:
            current += weight
            if roll <= current:
                return value

        return choices[-1][0]

    def _get_max_heroes(self, max_heroes: Optional[int]) -> int:
        if max_heroes is not None:
            return self._clamp(max_heroes, 1, 4)

        choices = [(int(k), v) for k, v in self.max_heroes_weights.items()]
        if not choices:
            return random.randint(1, 4)

        return self._clamp(self._weighted_choice_simple(choices), 1, 4)

    def _generate_context(self, subject: dict, location: dict, sub_location: dict, modifier: dict) -> dict:
        result = {}

        for lang in self.SUPPORTED_LANGUAGES:
            result[lang] = {
                "enemy": {
                    "details": self._localize_context_list(subject, "details", lang),
                    "behavior": self._localize_context_list(subject, "behavior", lang),
                    "attack": self._localize_context_list(subject, "attack", lang),
                },
                "place": {
                    "landmark": self._localize_context_list(location, "landmark", lang),
                    "feeling": self._localize_context_list(location, "feeling", lang),
                    "details": self._localize_context_list(sub_location, "details", lang),
                    "history": self._localize_context_list(sub_location, "history", lang),
                },
                "modifier": {
                    "details": self._localize_context_list(modifier, "details", lang),
                }
            }

        return result

    def _localize_context_list(self, data: dict, category: str, lang: str) -> list[str]:
        context = data.get("context", {})
        entries = context.get(category, [])

        result = []
        for entry in entries:
            if isinstance(entry, str):
                result.append(entry)
            elif isinstance(entry, dict):
                text = entry.get(lang) or entry.get("pt") or entry.get("en")
                if text:
                    result.append(text)

        return result

    def _get_location_with_preposition(self, sub_location: dict, preposition: str, lang: str) -> str:
        data = sub_location.get(lang, {})

        if isinstance(data, str):
            return data  # fallback simples

        # 1. Tenta versão pronta
        key = f"with_{preposition}"
        base = data.get("base") or data.get("text", "")

        if key in data:
            return f"{data[key]} {base}"

        if not base:
            return ""

        if lang != "pt":
            return base

        gender = sub_location.get("gender", "m")
        number = sub_location.get("number", "singular")

        if preposition == "em":
            if number == "plural":
                return f"nos {base}" if gender == "m" else f"nas {base}"
            else:
                return f"no {base}" if gender == "m" else f"na {base}"

        elif preposition == "de":
            if number == "plural":
                return f"dos {base}" if gender == "m" else f"das {base}"
            else:
                return f"do {base}" if gender == "m" else f"da {base}"

        elif preposition == "a":
            if number == "plural":
                return f"aos {base}" if gender == "m" else f"às {base}"
            else:
                return f"ao {base}" if gender == "m" else f"à {base}"

        return base

if __name__ == "__main__":
 
    # from kivy.app import App
    # from kivy.uix.boxlayout import BoxLayout
    # from kivy.uix.label import Label
    # from kivy.uix.button import Button
    # from kivy.uix.scrollview import ScrollView
    # class SimpleApp(App):
    #     def build(self):
    #         self.proc = ProceduralQuestSystem(language="pt")
    #         # Create a vertical layout
    #         layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

    #         # Initialize the Label
    #         self.my_label = Label(
    #             text="Name",
    #             halign="left",
    #             valign="top",
    #             text_size=(600, 20),
    #             font_size='20sp',
    #             size_hint_y=None,
    #             )
    #         self.my_label_2 = Label(
    #             text="description",
    #             halign="left",
    #             valign="top",
    #             text_size=(600, 100),
    #             font_size='20sp',
    #             size_hint_y=None,
    #             )
    #         self.my_label_4 = Label(
    #             text="Difficulty",
    #             halign="left",
    #             valign="top",
    #             text_size=(600, None),
    #             font_size='20sp',
    #             size_hint_y=None,
    #             )
    #         self.my_label_4.bind(
    #             texture_size=lambda instance, value: setattr(instance, 'height', value[1])
    #         )            
    #         self.my_label_4.bind(
    #             size=lambda instance, value: setattr(instance, 'text_size', (value[0] - 20, None))
    #         )

    #         self.scroll_label = ScrollView(size_hint=(1, 1))
    #         self.scroll_label.add_widget(self.my_label_4)

    #         layout.add_widget(self.my_label)
    #         layout.add_widget(self.my_label_2)
    #         layout.add_widget(self.scroll_label)

    #         # Initialize the Button and bind it to a function
    #         btn = Button(text="Click Me", size_hint_y=None, height=50)
    #         btn.bind(on_press=self.on_button_click)
    #         layout.add_widget(btn)

    #         return layout

    #     def on_button_click(self, instance):
    #         quest = self.proc.generate_quest_of_type("fight", 1)
    #         # Update label text when button is pressed
    #         self.my_label.text = f"Quest: {quest.name}"
    #         self.my_label_2.text = f"Description: {quest.description}"
    #         self.my_label_4.text = f"Difficulty: {quest.context}"

    # if __name__ == "__main__":
    #     SimpleApp().run()


    print("=" * 70)
    print("🎲 PROCEDURAL QUEST SYSTEM - TESTE")
    print("=" * 70)

    proc = ProceduralQuestSystem(language="pt")

    for _ in range(2):
        print("─" * 70)
        quest = proc.generate_quest_of_type("fight", 1)
        print(f"ID: {quest.id}")
        print(f"Nome: {quest.name}")
        print(f"Descrição: {quest.description}")
        # print(f"Dificuldade: {quest.difficulty}, max_heroes: {quest.max_heroes}, xp: {quest.rewards}, duration: {quest.duration} turns")
        print(f"Context: {quest.context}")
