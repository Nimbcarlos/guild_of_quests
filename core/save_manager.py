# core/save_manager.py
import json
import os

SAVE_DIR = "saves"

def save_game(manager, filename):
    """Salva o estado atual do jogo em um arquivo JSON."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, filename)

    # Serializa quests ativas: chaves como strings, heroes como lista de IDs
    active_quests_save = {}
    for qid, qdata in manager.active_quests.items():
        key = str(qid)
        active_quests_save[key] = {
            "turns_left": int(qdata.get("turns_left", 0)),
            "heroes": [h.id for h in qdata.get("heroes", [])],
        }

    # Serializa quests (para guardar available_since_turn)
    quests_save = {
        str(q.id): {
            "available_since_turn": getattr(q, "available_since_turn", None)
        }
        for q in manager.quests
    }

    data = {
        "current_turn": int(getattr(manager, "current_turn", 0)),
        "completed_quests": list(manager.completed_quests),
        "failed_quests": list(manager.failed_quests),
        "unlocked_heroes": list(manager.hero_manager.unlocked_heroes),
        "heroes": [
            {
                "id": h.id,
                "name": h.name,
                "xp": getattr(h, "xp", 0),
                "status": getattr(h, "status", "idle"),
            }
            for h in manager.hero_manager.all_heroes
        ],
        "active_quests": active_quests_save,
        "quests": quests_save,  # << salva estado extra das quests
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"💾 Jogo salvo em: {path}")


def load_game(manager, filename):
    """Carrega um save para o manager. Retorna True se carregou, False caso contrário."""
    path = os.path.join(SAVE_DIR, filename)

    if not os.path.exists(path):
        print(f"⚠️ Save '{filename}' não encontrado.")
        return False

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    manager.current_turn = data.get("current_turn", getattr(manager, "current_turn", 1))

    def _to_int_if_possible(x):
        try:
            return int(x)
        except Exception:
            return x

    manager.completed_quests = set(_to_int_if_possible(x) for x in data.get("completed_quests", []))
    manager.failed_quests = set(_to_int_if_possible(x) for x in data.get("failed_quests", []))
    manager.hero_manager.unlocked_heroes = set(_to_int_if_possible(x) for x in data.get("unlocked_heroes", []))

    # restaura atributos dos heróis
    for hero_data in data.get("heroes", []):
        hid = _to_int_if_possible(hero_data.get("id"))
        hero = manager.hero_manager.get_hero_by_id(hid)
        if hero:
            hero.xp = hero_data.get("xp", getattr(hero, "xp", 0))
            hero.status = hero_data.get("status", getattr(hero, "status", "idle"))

    # restaura quests ativas
    manager.active_quests = {}
    for qid_key, qdata in data.get("active_quests", {}).items():
        try:
            qid = int(qid_key)
        except Exception:
            qid = qid_key

        quest = manager.get_quest(qid)
        if quest is None:
            print(f"⚠️ Save refere-se à quest '{qid}' que não existe no catálogo atual — pulando.")
            continue

        heroes_list = []
        for hid in qdata.get("heroes", []):
            hid_conv = _to_int_if_possible(hid)
            hero_obj = manager.hero_manager.get_hero_by_id(hid_conv)
            if hero_obj:
                heroes_list.append(hero_obj)
                hero_obj.status = "on_mission"

        manager.active_quests[qid] = {
            "turns_left": int(qdata.get("turns_left", quest.duration)),
            "heroes": heroes_list,
        }

    # restaura available_since_turn das quests
    for qid_key, qextra in data.get("quests", {}).items():
        try:
            qid = int(qid_key)
        except Exception:
            qid = qid_key

        quest = manager.get_quest(qid)
        if quest:
            quest.available_since_turn = qextra.get("available_since_turn", None)

    print(f"📂 Jogo carregado de: {path}")
    return True
