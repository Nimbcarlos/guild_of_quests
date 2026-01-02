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
'''

heroes_folder = "data/heroes"
folder_path = Path(heroes_folder)

# Busca todos os arquivos .json na pasta
for json_file in sorted(folder_path.glob("*.json")):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            hero_data = json.load(f)
            print(hero_data["name"])
            print(hero_data["story"]['pt'])
            print(hero_data["perks"])
    except Exception as e:
        print(e)
'''


heroes_folder = "data/quests"
folder_path = Path(heroes_folder)

# Busca todos os arquivos .json na pasta
for json_file in sorted(folder_path.glob("*.json")):
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            hero_data = json.load(f)
            print(hero_data["id"])
            print(hero_data["name"]['pt'])
            print(hero_data["type"])
    except Exception as e:
        print(e)