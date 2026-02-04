import json
import os
from core.hero import Hero
from pathlib import Path

'''

OLD_BASE = "data/old"
HERO_BASE = "data/heroes"

LANGUAGES = ["en", "pt", "es", "ru", "zh", "ja"]

os.makedirs(HERO_BASE, exist_ok=True)

def load_json(path):
    if not os.path.exists(path):
        print("❌ Arquivo não existe:", path)
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

collector = {}

for lang in LANGUAGES:
    path = os.path.join(OLD_BASE, lang, "start_dialogues.json")
    print(f"\n📖 Lendo {path}")

    data = load_json(path)
    if not data:
        continue

    # 🔑 suporta os dois formatos
    heroes_block = data.get("heroes", data)

    for hero_id, hero_block in heroes_block.items():
        defaults = hero_block.get("default")

        if not isinstance(defaults, list):
            continue

        collector.setdefault(hero_id, {})
        collector[hero_id][lang] = defaults

        print(f"  ✔ Hero {hero_id} ({lang}) -> {len(defaults)} falas")

if not collector:
    print("\n⚠️ NENHUM DIÁLOGO COLETADO. Verifique o formato do JSON antigo.")
    exit()

for hero_id, lang_map in collector.items():
    hero_path = os.path.join(HERO_BASE, f"{hero_id}.json")
    hero_data = load_json(hero_path)

    hero_data.setdefault("start_dialogues", {})
    hero_data["start_dialogues"].setdefault("default", {})

    for lang, texts in lang_map.items():
        hero_data["start_dialogues"]["default"][lang] = texts

    save_json(hero_path, hero_data)
    print(f"💾 Hero {hero_id}.json salvo")
'''

heroes_folder = "data/heroes"
folder_path = Path(heroes_folder)

# # Busca todos os arquivos .json na pasta
# for json_file in sorted(folder_path.glob("*.json")):
#     try:
#         with open(json_file, "r", encoding="utf-8") as f:
#             hero_data = json.load(f)
#             print(hero_data["name"])
#             print(hero_data["hero_class"]["pt"])
#             # print(hero_data["story"]['pt'])
#             print(hero_data["perks"])
#     except Exception as e:
#         print(e)

quests_folder = "data/quests"
folder_path = Path(quests_folder)

# Busca todos os arquivos .json na pasta
for json_file in sorted(folder_path.glob("*.json")):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            quest_data = json.load(f)
            # if quest_data.get("duration") == 3:
            #     continue
            print(quest_data["id"])
            print(quest_data["name"]['pt'])
            print(quest_data["description"]['pt'])
            print(quest_data["type"])
            print("max_heroes", quest_data["max_heroes"])
            print("Quest que precisam estar completas", quest_data["required_quests"])
            print("quest que nao  podem estar completas:", quest_data["forbidden_quests"])
    except Exception as e:
        print(e)

'''


import json
from pathlib import Path

heroes_folder = "data/heroes"
quests_folder = "data/quests"

heroes_path = Path(heroes_folder)
quests_path = Path(quests_folder)

for hero_file in sorted(heroes_path.glob("*.json")):
    with open(hero_file, "r", encoding="utf-8") as f:
        hero_data = json.load(f)

    hero_name = hero_data["name"]["pt"] if isinstance(hero_data["name"], dict) else hero_data["name"]
    hero_perks = hero_data.get("perks", [])

    # Garante lista
    if not isinstance(hero_perks, list):
        hero_perks = [hero_perks]

    if hero_data["id"] != 1:
       continue

    print(f"\n🧙 Herói: {hero_name}")

    for quest_file in sorted(quests_path.glob("*.json")):
        with open(quest_file, "r", encoding="utf-8") as f:
            quest_data = json.load(f)

        quest_id = quest_data["id"]
        quest_name = quest_data["name"]["pt"] if isinstance(quest_data["name"], dict) else quest_data["name"]
        quest_type = quest_data.get("type", [])

        # Garante lista
        if not isinstance(quest_type, list):
            quest_type = [quest_type]

        # 🎯 Verifica interseção
        if set(hero_perks) & set(quest_type):
            print(f"  ✔ Pode fazer: {quest_id} {quest_name}")
'''

'''
import json
from pathlib import Path

# Mapeamento de quest_id para turno disponível
# Baseado na distribuição narrativa criada
QUEST_TURN_MAPPING = {
    # Turnos 1-10: Introdução
    14: 1,
    100: 2,
    1: 3,
    33: 4,
    51: 5,
    5: 6,
    15: 7,
    65: 8,
    25: 9,
    91: 10,
    
    # Turnos 11-25: Estabelecendo Perigos
    101: 11,
    2: 12,
    34: 13,
    150: 14,
    52: 15,
    88: 16,
    9: 17,
    43: 18,
    66: 19,
    4: 20,
    151: 21,
    102: 22,
    18: 23,
    61: 24,
    35: 25,
    
    # Turnos 26-40: Complicações Crescentes
    92: 26,
    7: 27,
    152: 28,
    103: 29,
    89: 30,
    53: 31,
    11: 32,
    67: 33,
    3: 34,
    153: 35,
    26: 36,
    104: 37,
    73: 38,
    36: 39,
    54: 40,
    
    # Turnos 41-50: Revelações e Clímax do Slime
    154: 41,
    93: 42,
    45: 43,
    155: 44,
    10: 45,
    82: 46,
    105: 47,
    16: 48,
    90: 49,
    106: 50,
    
    # Turnos 51-65: Arco dos Goblins Parte I
    120: 51,
    27: 52,
    55: 53,
    156: 54,
    68: 55,
    37: 56,
    6: 57,
    123: 58,
    74: 59,
    19: 60,
    157: 61,
    62: 62,
    124: 63,
    94: 64,
    38: 65,
    
    # Turnos 66-75: Arco dos Goblins Parte II
    125: 66,
    56: 67,
    158: 68,
    121: 69,
    22: 70,
    8: 71,
    126: 72,
    69: 73,
    122: 74,
    95: 75,
    
    # Turnos 76-85: Arco dos Goblins Parte III & Criaturas
    63: 76,
    159: 77,
    28: 78,
    127: 79,
    39: 80,
    160: 81,
    76: 82,
    128: 83,
    97: 84,
    161: 85,
    
    # Turnos 86-95: Conclusão Goblins & Início do Lich
    12: 86,
    162: 87,
    20: 88,
    129: 89,
    40: 90,
    163: 91,
    83: 92,
    164: 93,
    77: 94,
    165: 95,
    
    # Turnos 96-110: Arco do Lich Parte I
    130: 96,
    41: 97,
    166: 98,
    84: 99,
    135: 100,
    23: 101,
    131: 102,
    78: 103,
    57: 104,
    132: 105,
    42: 106,
    79: 107,
    133: 108,
    30: 109,
    134: 110,
    
    # Turnos 111-125: Arco do Lich Parte II
    85: 111,
    80: 112,
    136: 113,
    70: 114,
    81: 115,
    96: 116,
    21: 117,
    86: 118,
    71: 119,
    87: 120,
    58: 121,
    31: 122,
    98: 123,
    32: 124,
    24: 125,
    
    # Turnos 126-140: Missões Avançadas
    13: 126,
    46: 127,
    47: 128,
    48: 129,
    49: 130,
    50: 131,
    44: 132,
    64: 133,
    99: 134,
    72: 135,
    17: 136,
    59: 137,
    60: 138,
    # 29 e 75 reservados para expansão (139-140)
}

def update_quest_turns(quests_folder="data/quests"):
    """
    Atualiza o campo 'available_from_turn' de todos os arquivos JSON
    de quests baseado no mapeamento QUEST_TURN_MAPPING.
    """
    folder_path = Path(quests_folder)
    
    if not folder_path.exists():
        print(f"❌ Pasta '{quests_folder}' não encontrada!")
        return
    
    updated_count = 0
    not_found_count = 0
    error_count = 0
    
    print("🔄 Iniciando atualização dos turnos das quests...")
    print("=" * 60)
    
    # Busca todos os arquivos .json na pasta
    for json_file in sorted(folder_path.glob("*.json")):
        try:
            # Lê o arquivo JSON
            with open(json_file, "r", encoding="utf-8") as f:
                quest_data = json.load(f)
            
            quest_id = quest_data.get("id")
            quest_name = quest_data.get("name", {}).get("pt", "Nome não encontrado")
            
            # Verifica se a quest está no mapeamento
            if quest_id in QUEST_TURN_MAPPING:
                old_turn = quest_data.get("available_from_turn", "N/A")
                new_turn = QUEST_TURN_MAPPING[quest_id]
                
                # Atualiza o turno
                quest_data["available_from_turn"] = new_turn
                
                # Salva o arquivo atualizado
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(quest_data, f, ensure_ascii=False, indent=2)
                
                print(f"✅ Quest {quest_id:3d} - {quest_name[:40]:40s} | {old_turn:3} → {new_turn:3}")
                updated_count += 1
            else:
                print(f"⚠️  Quest {quest_id:3d} - {quest_name[:40]:40s} | NÃO MAPEADA")
                not_found_count += 1
                
        except Exception as e:
            print(f"❌ Erro ao processar {json_file.name}: {e}")
            error_count += 1
    
    print("=" * 60)
    print(f"\n📊 Resumo da atualização:")
    print(f"   ✅ Quests atualizadas: {updated_count}")
    print(f"   ⚠️  Quests não mapeadas: {not_found_count}")
    print(f"   ❌ Erros: {error_count}")
    print(f"\n🎉 Atualização concluída!")

def verify_quest_turns(quests_folder="data/quests"):
    """
    Verifica se todas as quests têm turnos válidos e exibe um resumo.
    """
    folder_path = Path(quests_folder)
    
    if not folder_path.exists():
        print(f"❌ Pasta '{quests_folder}' não encontrada!")
        return
    
    print("\n🔍 Verificando turnos das quests...")
    print("=" * 60)
    
    quests_by_turn = {}
    
    for json_file in sorted(folder_path.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                quest_data = json.load(f)
            
            quest_id = quest_data.get("id")
            quest_name = quest_data.get("name", {}).get("pt", "")
            turn = quest_data.get("available_from_turn", -1)
            
            if turn not in quests_by_turn:
                quests_by_turn[turn] = []
            
            quests_by_turn[turn].append(f"Quest {quest_id} - {quest_name}")
            
        except Exception as e:
            print(f"❌ Erro ao verificar {json_file.name}: {e}")
    
    # Exibe resumo por turno
    for turn in sorted(quests_by_turn.keys()):
        if turn == -1:
            print(f"\n⚠️  QUESTS SEM TURNO DEFINIDO:")
        else:
            print(f"\n📅 Turno {turn}:")
        
        for quest in quests_by_turn[turn]:
            print(f"   • {quest}")
    
    print("=" * 60)

def list_unmapped_quests(quests_folder="data/quests"):
    """
    Lista todas as quests que não estão no mapeamento.
    """
    folder_path = Path(quests_folder)
    
    if not folder_path.exists():
        print(f"❌ Pasta '{quests_folder}' não encontrada!")
        return
    
    print("\n🔍 Quests não mapeadas:")
    print("=" * 60)
    
    unmapped = []
    
    for json_file in sorted(folder_path.glob("*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                quest_data = json.load(f)
            
            quest_id = quest_data.get("id")
            quest_name = quest_data.get("name", {}).get("pt", "")
            
            if quest_id not in QUEST_TURN_MAPPING:
                unmapped.append((quest_id, quest_name))
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    if unmapped:
        for quest_id, quest_name in unmapped:
            print(f"   Quest {quest_id:3d} - {quest_name}")
        print(f"\n   Total: {len(unmapped)} quests não mapeadas")
    else:
        print("   ✅ Todas as quests estão mapeadas!")
    
    print("=" * 60)

if __name__ == "__main__":
    # Executa a atualização
    update_quest_turns()
    
    # Verifica se há quests não mapeadas
    print("\n")
    list_unmapped_quests()
    
    # Opcional: verificar distribuição por turno
    # verify_quest_turns()
'''



'''
# atualiza campos
import json
from pathlib import Path

quests_folder = "data/quests"
folder_path = Path(quests_folder)

for json_file in sorted(folder_path.glob("*.json")):
    try:
        # Lê o arquivo JSON
        with open(json_file, "r", encoding="utf-8") as f:
            quest_data = json.load(f)
            
        # Atualiza o turno
        quest_data["duration"] = 3
        
        # Salva o arquivo atualizado
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(quest_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"❌ Erro ao processar {json_file.name}: {e}")
'''