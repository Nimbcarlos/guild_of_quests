# core/save_manager.py
import json
import os

SAVE_DIR = "saves"

def save_game(manager, filename):
    """Salva o estado atual do jogo em um arquivo JSON (versão otimizada)."""
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

    # Serializa quests concluídas com os heróis que participaram
    completed_quests_save = {
        str(qid): list(hids)
        for qid, hids in getattr(manager, "completed_quests", {}).items()
    }

    # 🔹 OTIMIZADO: Salva apenas quests que têm available_since_turn definido
    # Formato compacto: {"quest_id": turno}
    quests_availability = {
        str(q.id): getattr(q, "available_since_turn", None)
        for q in manager.quests
        if getattr(q, "available_since_turn", None) is not None
    }

    data = {
        "current_turn": int(getattr(manager, "current_turn", 0)),
        "completed_quests": completed_quests_save,
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
        "quests_availability": quests_availability,  # ← Novo formato compacto
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

    # Carrega quests concluídas (dict quest_id -> set de heróis)
    raw_completed = data.get("completed_quests", {})
    manager.completed_quests = {
        _to_int_if_possible(qid): set(_to_int_if_possible(h) for h in hlist)
        for qid, hlist in raw_completed.items()
    }

    manager.failed_quests = set(_to_int_if_possible(x) for x in data.get("failed_quests", []))
    manager.hero_manager.unlocked_heroes = set(_to_int_if_possible(x) for x in data.get("unlocked_heroes", []))

    # Restaura atributos dos heróis
    for hero_data in data.get("heroes", []):
        hid = _to_int_if_possible(hero_data.get("id"))
        hero = manager.hero_manager.get_hero_by_id(hid)
        if hero:
            hero.xp = hero_data.get("xp", getattr(hero, "xp", 0))
            hero.status = hero_data.get("status", getattr(hero, "status", "idle"))

    # Restaura quests ativas
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

    # 🔹 OTIMIZADO: Restaura available_since_turn (formato compacto)
    # Suporta tanto o formato antigo quanto o novo
    quests_data = data.get("quests_availability") or data.get("quests", {})
    
    for qid_key, turn_value in quests_data.items():
        try:
            qid = int(qid_key)
        except Exception:
            qid = qid_key

        quest = manager.get_quest(qid)
        if quest:
            # Formato novo: {"quest_id": turno}
            if isinstance(turn_value, int):
                quest.available_since_turn = turn_value
            # Formato antigo: {"quest_id": {"available_since_turn": turno}}
            elif isinstance(turn_value, dict):
                quest.available_since_turn = turn_value.get("available_since_turn", None)

    # Revalida quests após carregar
    manager._revalidate_available_quests()
    
    # Marca que a assistente não deve falar como "primeira vez"
    if hasattr(manager, 'assistant'):
        manager.assistant.first_time = False

    print(f"📂 Jogo carregado de: {path}")
    return True


# ═══════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES (mantidas iguais)
# ═══════════════════════════════════════════════════════════

def list_saves():
    """
    Lista todos os arquivos de save disponíveis.
    
    Returns:
        list: Lista com nomes dos arquivos de save (.json)
    """
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)
        return []
    
    files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.json')]
    
    files.sort(
        key=lambda f: os.path.getmtime(os.path.join(SAVE_DIR, f)),
        reverse=True
    )
    
    return files


def delete_save(filename):
    """
    Deleta um arquivo de save.
    
    Args:
        filename (str): Nome do arquivo a ser deletado
        
    Returns:
        bool: True se deletado com sucesso, False caso contrário
    """
    filepath = os.path.join(SAVE_DIR, filename)
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"✅ Save '{filename}' deletado com sucesso")
            return True
        else:
            print(f"⚠️ Arquivo '{filename}' não encontrado")
            return False
    except Exception as e:
        print(f"❌ Erro ao deletar save: {e}")
        return False


def get_save_info(filename):
    """
    Obtém informações sobre um save (turno, quests completadas, etc).
    
    Args:
        filename (str): Nome do arquivo de save
        
    Returns:
        dict: Dicionário com informações do save ou None se erro
    """
    filepath = os.path.join(SAVE_DIR, filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return {
            'turn': data.get('current_turn', 0),
            'completed_quests': len(data.get('completed_quests', [])),
            'active_quests': len(data.get('active_quests', {})),
            'failed_quests': len(data.get('failed_quests', [])),
        }
    except Exception as e:
        print(f"Erro ao ler info do save '{filename}': {e}")
        return None

def get_latest_save():
    saves = list_saves()
    return saves[0] if saves else None