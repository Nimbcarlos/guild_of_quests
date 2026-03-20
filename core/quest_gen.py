# ════════════════════════════════════════════════════════════════
# 🎲 SISTEMA PROCEDURAL - SAVE/LOAD POR SEEDS
# ════════════════════════════════════════════════════════════════
#
# Sistema onde:
# • Seed determina TUDO (nome, descrição, contexto, dificuldade)
# • Save grava apenas as seeds geradas
# • Load reconstrói quests exatamente iguais
# • Pode gerar quest de tipo específico
#
# ════════════════════════════════════════════════════════════════

import random
import json
from typing import List, Dict, Optional, Literal
from pathlib import Path

# ════════════════════════════════════════════════════════════════
# 📊 BANCO DE DADOS DE COMPONENTES POR TIPO
# ════════════════════════════════════════════════════════════════

QUEST_COMPONENTS = {
    # ──────────────────────────────────────────────────────────
    # FIGHT - Verbos de combate
    # ──────────────────────────────────────────────────────────
    "fight": {
        "verbs": {
            1: {"pt": "Derrotar", "en": "Defeat", "es": "Derrotar", "difficulty": 1.0},
            2: {"pt": "Eliminar", "en": "Eliminate", "es": "Eliminar", "difficulty": 1.2},
            3: {"pt": "Caçar", "en": "Hunt", "es": "Cazar", "difficulty": 0.9},
            4: {"pt": "Repelir", "en": "Repel", "es": "Repeler", "difficulty": 1.1},
        }
    },
    
    # ──────────────────────────────────────────────────────────
    # DIPLOMACY - Verbos de negociação
    # ──────────────────────────────────────────────────────────
    "diplomacy": {
        "verbs": {
            1: {"pt": "Negociar com", "en": "Negotiate with", "es": "Negociar con", "difficulty": 0.8},
            2: {"pt": "Convencer", "en": "Convince", "es": "Convencer", "difficulty": 1.0},
            3: {"pt": "Mediar conflito com", "en": "Mediate conflict with", "es": "Mediar conflicto con", "difficulty": 1.1},
        }
    },
    
    # ──────────────────────────────────────────────────────────
    # NATURE - Verbos de natureza
    # ──────────────────────────────────────────────────────────
    "nature": {
        "verbs": {
            1: {"pt": "Explorar", "en": "Explore", "es": "Explorar", "difficulty": 0.7},
            2: {"pt": "Purificar", "en": "Purify", "es": "Purificar", "difficulty": 1.3},
            3: {"pt": "Restaurar", "en": "Restore", "es": "Restaurar", "difficulty": 1.0},
        }
    },
    
    # ──────────────────────────────────────────────────────────
    # ATHLETICS - Verbos de atletismo
    # ──────────────────────────────────────────────────────────
    "athletics": {
        "verbs": {
            1: {"pt": "Escalar", "en": "Climb", "es": "Escalar", "difficulty": 0.9},
            2: {"pt": "Atravessar", "en": "Cross", "es": "Atravesar", "difficulty": 1.0},
            3: {"pt": "Escapar de", "en": "Escape from", "es": "Escapar de", "difficulty": 1.2},
        }
    },
    
    # ──────────────────────────────────────────────────────────
    # THIEVERY - Verbos furtivos
    # ──────────────────────────────────────────────────────────
    "thievery": {
        "verbs": {
            1: {"pt": "Infiltrar", "en": "Infiltrate", "es": "Infiltrar", "difficulty": 1.4},
            2: {"pt": "Roubar de", "en": "Steal from", "es": "Robar de", "difficulty": 1.5},
            3: {"pt": "Sabotar", "en": "Sabotage", "es": "Sabotear", "difficulty": 1.3},
        }
    },
    
    # ──────────────────────────────────────────────────────────
    # RELIGION - Verbos religiosos
    # ──────────────────────────────────────────────────────────
    "religion": {
        "verbs": {
            1: {"pt": "Consagrar", "en": "Consecrate", "es": "Consagrar", "difficulty": 1.1},
            2: {"pt": "Exorcizar", "en": "Exorcize", "es": "Exorcizar", "difficulty": 1.6},
            3: {"pt": "Abençoar", "en": "Bless", "es": "Bendecir", "difficulty": 0.9},
        }
    },
    
    # ──────────────────────────────────────────────────────────
    # ARCANA - Verbos mágicos
    # ──────────────────────────────────────────────────────────
    "arcana": {
        "verbs": {
            1: {"pt": "Investigar", "en": "Investigate", "es": "Investigar", "difficulty": 1.2},
            2: {"pt": "Desfazer magia de", "en": "Dispel magic from", "es": "Disipar magia de", "difficulty": 1.4},
            3: {"pt": "Estudar", "en": "Study", "es": "Estudiar", "difficulty": 0.8},
        }
    },
    
    # ──────────────────────────────────────────────────────────
    # COMPONENTES COMPARTILHADOS (todos os tipos)
    # ──────────────────────────────────────────────────────────
    "shared": {
        "targets": {
            1: {"pt": "orcs", "en": "orcs", "es": "orcos", "power": 1.0},
            2: {"pt": "goblins", "en": "goblins", "es": "goblins", "power": 0.7},
            3: {"pt": "bandidos", "en": "bandits", "es": "bandidos", "power": 0.8},
            4: {"pt": "lobos", "en": "wolves", "es": "lobos", "power": 0.6},
            5: {"pt": "espíritos", "en": "spirits", "es": "espíritus", "power": 1.2},
            6: {"pt": "trolls", "en": "trolls", "es": "trolls", "power": 1.5},
            7: {"pt": "mortos-vivos", "en": "undead", "es": "no-muertos", "power": 1.3},
            8: {"pt": "cultistas", "en": "cultists", "es": "cultistas", "power": 1.1},
            9: {"pt": "demônios", "en": "demons", "es": "demonios", "power": 2.0},
            10: {"pt": "dragões", "en": "dragons", "es": "dragones", "power": 2.5},
            11: {"pt": "aldeões", "en": "villagers", "es": "aldeanos", "power": 0.5},
            12: {"pt": "mercadores", "en": "merchants", "es": "mercaderes", "power": 0.6},
            13: {"pt": "druidas", "en": "druids", "es": "druidas", "power": 1.0},
        },
        
        "locations": {
            1: {"pt": "da planície", "en": "of the plains", "es": "de la llanura", "danger": 0.8},
            2: {"pt": "da floresta", "en": "of the forest", "es": "del bosque", "danger": 1.0},
            3: {"pt": "da montanha", "en": "of the mountain", "es": "de la montaña", "danger": 1.2},
            4: {"pt": "do pântano", "en": "of the swamp", "es": "del pantano", "danger": 1.3},
            5: {"pt": "da caverna", "en": "of the cave", "es": "de la cueva", "danger": 1.4},
            6: {"pt": "das ruínas", "en": "of the ruins", "es": "de las ruinas", "danger": 1.5},
            7: {"pt": "do vulcão", "en": "of the volcano", "es": "del volcán", "danger": 2.0},
            8: {"pt": "do deserto", "en": "of the desert", "es": "del desierto", "danger": 1.1},
            9: {"pt": "da tundra", "en": "of the tundra", "es": "de la tundra", "danger": 1.3},
            10: {"pt": "da cidade", "en": "of the city", "es": "de la ciudad", "danger": 0.7},
        },
        
        "modifiers": {
            1: {"pt": "corrompidos", "en": "corrupted", "es": "corrompidos", "difficulty_add": 0.3},
            2: {"pt": "selvagens", "en": "wild", "es": "salvajes", "difficulty_add": 0.2},
            3: {"pt": "anciões", "en": "ancient", "es": "ancianos", "difficulty_add": 0.5},
            4: {"pt": "furiosos", "en": "enraged", "es": "furiosos", "difficulty_add": 0.4},
            5: {"pt": "amaldiçoados", "en": "cursed", "es": "malditos", "difficulty_add": 0.6},
            6: {"pt": "misteriosos", "en": "mysterious", "es": "misteriosos", "difficulty_add": 0.1},
        }
    }
}


# ════════════════════════════════════════════════════════════════
# 🎲 GERADOR PROCEDURAL COM SAVE/LOAD
# ════════════════════════════════════════════════════════════════

QuestType = Literal["fight", "diplomacy", "nature", "athletics", "thievery", "religion", "arcana"]

class ProceduralQuestSystem:
    """
    Sistema procedural onde seed determina TUDO.
    
    FORMATO DA SEED: TTVVTTLLMM (10 dígitos)
    ────────────────────────────────────────
    TT = Tipo (01=fight, 02=diplomacy, etc)
    VV = Verbo dentro do tipo (01-04)
    TT = Target/Alvo (01-13)
    LL = Local (01-10)
    MM = Modificador (01-06)
    
    EXEMPLO: 0101020304
    ──────────────────
    01 = fight
    01 = Derrotar
    02 = goblins
    03 = montanha
    04 = furiosos
    
    ➡️  Quest de fight: "Derrotar goblins furiosos da montanha"
    """
    
    # Mapa de tipo para ID
    TYPE_MAP = {
        "fight": 1,
        "diplomacy": 2,
        "nature": 3,
        "athletics": 4,
        "thievery": 5,
        "religion": 6,
        "arcana": 7,
    }
    
    # Mapa reverso
    ID_TO_TYPE = {v: k for k, v in TYPE_MAP.items()}
    
    def __init__(self, language="pt"):
        self.language = language
        self.db = QUEST_COMPONENTS
    
    # ════════════════════════════════════════════════════════════
    # GERAÇÃO DE SEEDS
    # ════════════════════════════════════════════════════════════
    
    def generate_seed(
        self, 
        quest_type: QuestType,
        verb_id: Optional[int] = None,
        target_id: Optional[int] = None,
        location_id: Optional[int] = None,
        modifier_id: Optional[int] = None
    ) -> int:
        """
        Gera uma seed para quest de tipo específico.
        
        Args:
            quest_type: Tipo da quest (fight, diplomacy, etc)
            verb_id: ID do verbo (ou None para aleatório)
            target_id: ID do alvo (ou None para aleatório)
            location_id: ID do local (ou None para aleatório)
            modifier_id: ID do modificador (ou None para aleatório)
        
        Returns:
            Seed (10 dígitos): TTVVTTLLMM
        """
        # Converte tipo para ID
        type_id = self.TYPE_MAP[quest_type]
        
        # Gera IDs aleatórios se não fornecidos
        if verb_id is None:
            max_verb = max(self.db[quest_type]["verbs"].keys())
            verb_id = random.randint(1, max_verb)
        
        if target_id is None:
            target_id = random.randint(1, 13)
        
        if location_id is None:
            location_id = random.randint(1, 10)
        
        if modifier_id is None:
            modifier_id = random.randint(1, 6)
        
        # Combina em seed de 10 dígitos
        seed = int(f"{type_id:02d}{verb_id:02d}{target_id:02d}{location_id:02d}{modifier_id:02d}")
        
        return seed
    
    def decode_seed(self, seed: int) -> Dict:
        """
        Decodifica uma seed em seus componentes.
        
        Args:
            seed: Seed (formato TTVVTTLLMM)
        
        Returns:
            Dict com type, verb_id, target_id, location_id, modifier_id
        """
        seed_str = f"{seed:010d}"
        
        type_id = int(seed_str[0:2])
        verb_id = int(seed_str[2:4])
        target_id = int(seed_str[4:6])
        location_id = int(seed_str[6:8])
        modifier_id = int(seed_str[8:10])
        
        quest_type = self.ID_TO_TYPE.get(type_id)
        
        return {
            "type": quest_type,
            "type_id": type_id,
            "verb_id": verb_id,
            "target_id": target_id,
            "location_id": location_id,
            "modifier_id": modifier_id
        }
    
    # ════════════════════════════════════════════════════════════
    # RECONSTRUÇÃO DE QUEST A PARTIR DE SEED
    # ════════════════════════════════════════════════════════════
    
    def reconstruct_quest_from_seed(self, seed: int) -> Dict:
        """
        Reconstrói TODA a quest a partir da seed.
        
        Esta é a função principal para LOAD - dado uma seed,
        reconstrói exatamente a mesma quest que foi gerada.
        
        Args:
            seed: Seed da quest
        
        Returns:
            Dict completo com todos os dados da quest
        """
        # Decodifica seed
        components = self.decode_seed(seed)
        
        quest_type = components["type"]
        verb_id = components["verb_id"]
        target_id = components["target_id"]
        location_id = components["location_id"]
        modifier_id = components["modifier_id"]
        
        # Busca componentes
        verb = self.db[quest_type]["verbs"].get(verb_id)
        target = self.db["shared"]["targets"].get(target_id)
        location = self.db["shared"]["locations"].get(location_id)
        modifier = self.db["shared"]["modifiers"].get(modifier_id)
        
        if not all([verb, target, location, modifier]):
            raise ValueError(f"Seed inválida: {seed}")
        
        # ──────────────────────────────────────────────────────
        # MONTA QUEST COMPLETA
        # ──────────────────────────────────────────────────────
        
        # Nome (multilíngue)
        name = {
            "pt": f"{verb['pt']} {target['pt']} {modifier['pt']} {location['pt']}",
            "en": f"{verb['en']} {modifier['en']} {target['en']} {location['en']}",
            "es": f"{verb['es']} {target['es']} {modifier['es']} {location['es']}"
        }
        
        # Descrição
        description = self._generate_description(quest_type, verb, target, location, modifier)
        
        # Dificuldade
        difficulty = self._calculate_difficulty(verb, target, location, modifier)
        
        # Contexto
        context = {
            "location": location[self.language],
            "enemy": target[self.language],
            "enemy_type": modifier[self.language]
        }
        
        # Conclusão
        conclusion = self._generate_conclusion(quest_type, target, location, modifier)
        
        # ──────────────────────────────────────────────────────
        # RETORNA DADOS COMPLETOS
        # ──────────────────────────────────────────────────────
        return {
            "seed": seed,  # ✅ Importante para save!
            "id": f"proc_{seed}",
            "name": name,
            "description": description,
            "type": quest_type,
            "max_heroes": self._calculate_max_heroes(difficulty),
            "expired_at": 5,
            "available_from_turn": 1,
            "duration": self._calculate_duration(difficulty),
            "difficulty": int(difficulty),
            "rewards": {"xp": int(50 * difficulty)},
            "required_quests": [],
            "forbidden_quests": [],
            "required_perks": [quest_type],
            "context": context,
            "conclusion": conclusion,
            "is_procedural": True  # ✅ Marca como procedural
        }
    
    # ════════════════════════════════════════════════════════════
    # GERAÇÃO POR TIPO
    # ════════════════════════════════════════════════════════════
    
    def generate_quest_of_type(self, quest_type: QuestType) -> Dict:
        """
        Gera uma quest aleatória de tipo específico.
        
        Args:
            quest_type: Tipo desejado (fight, diplomacy, etc)
        
        Returns:
            Dict completo da quest
        """
        seed = self.generate_seed(quest_type)
        return self.reconstruct_quest_from_seed(seed)
    
    # ════════════════════════════════════════════════════════════
    # FUNÇÕES AUXILIARES
    # ════════════════════════════════════════════════════════════
    
    def _calculate_difficulty(self, verb, target, location, modifier) -> float:
        """Calcula dificuldade baseada nos componentes."""
        base = 1.0
        difficulty = (
            base * 
            verb["difficulty"] * 
            target["power"] * 
            location["danger"]
        ) + modifier["difficulty_add"]
        
        return round(difficulty, 1)
    
    def _calculate_max_heroes(self, difficulty: float) -> int:
        """Calcula max_heroes baseado na dificuldade."""
        if difficulty < 1.0:
            return 1
        elif difficulty < 1.5:
            return 2
        elif difficulty < 2.0:
            return 3
        else:
            return 4
    
    def _calculate_duration(self, difficulty: float) -> int:
        """Calcula duração baseada na dificuldade."""
        return max(2, min(5, int(difficulty * 2)))
    
    def _generate_description(self, quest_type, verb, target, location, modifier) -> Dict:
        """Gera descrição procedural."""
        templates = {
            "fight": {
                "pt": f"Um grupo de {target['pt']} {modifier['pt']} foi avistado {location['pt']}. Eles representam uma ameaça e devem ser eliminados antes que causem mais destruição.",
                "en": f"A group of {modifier['en']} {target['en']} has been spotted {location['en']}. They pose a threat and must be eliminated before they cause more destruction.",
                "es": f"Un grupo de {target['es']} {modifier['es']} ha sido avistado {location['es']}. Representan una amenaza y deben ser eliminados antes de que causen más destrucción."
            },
            "diplomacy": {
                "pt": f"Os {target['pt']} {location['pt']} estão se tornando {modifier['pt']}. Uma solução diplomática urgente é necessária para evitar confronto.",
                "en": f"The {target['en']} {location['en']} are becoming {modifier['en']}. An urgent diplomatic solution is needed to avoid confrontation.",
                "es": f"Los {target['es']} {location['es']} se están volviendo {modifier['es']}. Se necesita una solución diplomática urgente para evitar el enfrentamiento."
            },
            "nature": {
                "pt": f"A natureza {location['pt']} foi afetada por forças {modifier['pt']}. O equilíbrio natural deve ser restaurado rapidamente.",
                "en": f"The nature {location['en']} has been affected by {modifier['en']} forces. The natural balance must be quickly restored.",
                "es": f"La naturaleza {location['es']} ha sido afectada por fuerzas {modifier['es']}. El equilibrio natural debe ser restaurado rápidamente."
            },
            "athletics": {
                "pt": f"Um caminho {modifier['pt']} {location['pt']} precisa ser atravessado. Apenas os mais ágeis e resistentes conseguirão completar esta jornada.",
                "en": f"A {modifier['en']} path {location['en']} needs to be crossed. Only the most agile and resilient will complete this journey.",
                "es": f"Un camino {modifier['es']} {location['es']} necesita ser atravesado. Solo los más ágiles y resistentes completarán este viaje."
            },
            "thievery": {
                "pt": f"Uma operação furtiva {location['pt']} é necessária. Os {target['pt']} {modifier['pt']} guardam algo de grande valor que deve ser recuperado discretamente.",
                "en": f"A stealth operation {location['en']} is needed. The {modifier['en']} {target['en']} guard something of great value that must be discreetly recovered.",
                "es": f"Se necesita una operación sigilosa {location['es']}. Los {target['es']} {modifier['es']} guardan algo de gran valor que debe ser recuperado discretamente."
            },
            "religion": {
                "pt": f"Um local sagrado {location['pt']} foi profanado por forças {modifier['pt']}. A purificação espiritual é essencial para restaurar a santidade.",
                "en": f"A sacred place {location['en']} has been desecrated by {modifier['en']} forces. Spiritual purification is essential to restore sanctity.",
                "es": f"Un lugar sagrado {location['es']} ha sido profanado por fuerzas {modifier['es']}. La purificación espiritual es esencial para restaurar la santidad."
            },
            "arcana": {
                "pt": f"Energias arcanas {modifier['pt']} foram detectadas {location['pt']}. Uma investigação mágica detalhada é necessária para compreender a fonte.",
                "en": f"{modifier['en'].capitalize()} arcane energies have been detected {location['en']}. A detailed magical investigation is needed to understand the source.",
                "es": f"Energías arcanas {modifier['es']} han sido detectadas {location['es']}. Se necesita una investigación mágica detallada para comprender la fuente."
            }
        }
        
        return templates.get(quest_type, templates["fight"])
    
    def _generate_conclusion(self, quest_type, target, location, modifier) -> Dict:
        """Gera textos de conclusão."""
        return {
            "success": {
                "pt": f"Os {target['pt']} {modifier['pt']} {location['pt']} foram derrotados com sucesso!",
                "en": f"The {modifier['en']} {target['en']} {location['en']} have been successfully defeated!",
                "es": f"¡Los {target['es']} {modifier['es']} {location['es']} han sido derrotados con éxito!"
            },
            "failure": {
                "pt": f"A missão {location['pt']} fracassou. Os {target['pt']} permanecem uma ameaça.",
                "en": f"The mission {location['en']} has failed. The {target['en']} remain a threat.",
                "es": f"La misión {location['es']} ha fracasado. Los {target['es']} siguen siendo una amenaza."
            }
        }


# ════════════════════════════════════════════════════════════════
# 💾 INTEGRAÇÃO COM SAVE/LOAD
# ════════════════════════════════════════════════════════════════

class ProceduralQuestSaveSystem:
    """
    Gerencia save/load de quests procedurais.
    
    SAVE: Armazena apenas as seeds
    LOAD: Reconstrói quests a partir das seeds
    """
    
    @staticmethod
    def save_procedural_quests(active_quests: Dict, completed_seeds: set, filepath: str):
        """
        Salva quests procedurais (apenas seeds).
        
        Args:
            active_quests: Dict de quests ativas {seed: quest_data}
            completed_seeds: Set de seeds completadas
            filepath: Caminho do arquivo de save
        """
        data = {
            "active_procedural_quests": {
                str(seed): {
                    "seed": seed,
                    "turns_left": quest_data.get("turns_left", 0),
                    "heroes": quest_data.get("heroes", [])
                }
                for seed, quest_data in active_quests.items()
                if isinstance(seed, int)  # Só quests procedurais
            },
            "completed_procedural_seeds": list(completed_seeds)
        }
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_procedural_quests(filepath: str, generator: ProceduralQuestSystem) -> tuple:
        """
        Carrega quests procedurais (reconstrói a partir de seeds).
        
        Args:
            filepath: Caminho do arquivo de save
            generator: Instância do ProceduralQuestSystem
        
        Returns:
            (active_quests_dict, completed_seeds_set)
        """
        if not Path(filepath).exists():
            return {}, set()
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Reconstrói quests ativas
        active = {}
        for seed_str, quest_data in data.get("active_procedural_quests", {}).items():
            seed = int(seed_str)
            
            # ✅ RECONSTRÓI a quest a partir da seed
            reconstructed = generator.reconstruct_quest_from_seed(seed)
            
            # Adiciona dados específicos do save
            reconstructed["turns_left"] = quest_data.get("turns_left", 0)
            reconstructed["heroes"] = quest_data.get("heroes", [])
            
            active[seed] = reconstructed
        
        # Carrega seeds completadas
        completed = set(data.get("completed_procedural_seeds", []))
        
        return active, completed


# ════════════════════════════════════════════════════════════════
# 🧪 TESTE
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("🎲 SISTEMA PROCEDURAL - SAVE/LOAD POR SEEDS")
    print("=" * 70)
    
    gen = ProceduralQuestSystem(language="pt")
    
    # ──────────────────────────────────────────────────────────
    # TESTE 1: Gera quest de tipo específico
    # ──────────────────────────────────────────────────────────
    print("\n1️⃣  Gerando quest de FIGHT:")
    print("─" * 70)
    
    fight_quest = gen.generate_quest_of_type("fight")
    print(f"Seed: {fight_quest['seed']}")
    print(f"Nome: {fight_quest['name']['pt']}")
    print(f"Tipo: {fight_quest['type']}")
    print(f"Contexto: {fight_quest['context']}")
    
    # ──────────────────────────────────────────────────────────
    # TESTE 2: Reconstrói a MESMA quest da seed
    # ──────────────────────────────────────────────────────────
    print("\n2️⃣  Reconstruindo quest a partir da seed:")
    print("─" * 70)
    
    saved_seed = fight_quest['seed']
    print(f"Seed salva: {saved_seed}")
    
    # "Carrega" a quest (reconstrói)
    loaded_quest = gen.reconstruct_quest_from_seed(saved_seed)
    
    print(f"Quest reconstruída: {loaded_quest['name']['pt']}")
    print(f"Contexto: {loaded_quest['context']}")
    print(f"✅ Quests são idênticas: {fight_quest['name'] == loaded_quest['name']}")
    
    # ──────────────────────────────────────────────────────────
    # TESTE 3: Gera quests de tipos diferentes
    # ──────────────────────────────────────────────────────────
    print("\n3️⃣  Gerando quests de tipos diferentes:")
    print("─" * 70)
    
    for quest_type in ["diplomacy", "nature", "thievery"]:
        quest = gen.generate_quest_of_type(quest_type)
        print(f"{quest_type.upper()}: {quest['name']['pt']} (seed: {quest['seed']})")
    
    print("\n" + "=" * 70)