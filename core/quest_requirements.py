def check_available_turn(quest, manager) -> bool:
    available_from_turn = getattr(quest, "available_from_turn", None)
    if available_from_turn is None:
        return True
    return manager.current_turn >= available_from_turn


def check_required_quests(quest, manager) -> bool:
    required_quests = getattr(quest, "required_quests", [])
    forbidden_quests = getattr(quest, "forbidden_quests", [])
    required_heroes = getattr(quest, "required_heroes", [])
    forbidden_heroes = getattr(quest, "forbidden_heroes", [])

    # 1 — Verifica se required_quests foram concluídas
    if required_quests:
        quest_requirement_met = False

        for req in required_quests:
            req_str = str(req).strip()

            # AND → "10_12_15"
            if "_" in req_str:
                ids_needed = [int(qid) for qid in req_str.split("_")]
                if all(qid in manager.completed_quests for qid in ids_needed):
                    quest_requirement_met = True

            # OR → simples "10"
            else:
                if int(req_str) in manager.completed_quests:
                    quest_requirement_met = True

        if not quest_requirement_met:
            return False

    # 3 — Forbidden Quests
    for fquest in forbidden_quests:
        if int(fquest) in manager.completed_quests:
            return False

    # 2 — Required Heroes (agora com O, E e combos)
    if required_heroes:
        # Pega todos os heróis que completaram cada quest requerida
        # (Normalmente só tem uma quest requerida, mas mantemos compatível)
        completed_by_all = set()
        for req in required_quests:
            completed_by_all |= manager.completed_quests.get(req, set())

        # 🎯 NOVA LÓGICA:
        # Basta UM dos requisitos ser atendido!
        requirement_met = False

        for hero_req in required_heroes:
            hero_req_str = str(hero_req)

            # Caso "AND" → 1_2_3
            if "_" in hero_req_str:
                ids_needed = [int(h.strip()) for h in hero_req_str.split("_")]
                if all(hid in completed_by_all for hid in ids_needed):
                    requirement_met = True

            # Caso simples → OR
            else:
                if int(hero_req_str) in completed_by_all:
                    requirement_met = True
        
        # Se nenhum requisito foi atendido → falha
        if not requirement_met:
            return False

    # 3 — Forbidden Heroes
    if forbidden_heroes:
        for req in required_quests:
            completed_by = manager.completed_quests.get(req, set())
            for forbidden_id in forbidden_heroes:
                if forbidden_id in completed_by:
                    return False

    return True


def check_trigger_on_fail(quest, manager) -> bool:
    """Verifica se a quest é liberada apenas se outras falharem."""
    trigger = getattr(quest, "trigger_on_fail", [])
    if not trigger:
        return True  # não depende de falha
    return any(failed in manager.failed_quests for failed in trigger)


def check_not_completed(quest, manager) -> bool:
    """Garante que a quest ainda não foi concluída."""
    return quest.id not in manager.completed_quests


# Exemplo: requisito de nível mínimo dos heróis
def check_min_hero_level(quest, manager) -> bool:
    min_level = getattr(quest, "min_level", None)
    if not min_level:
        return True
    # Se pelo menos um herói desbloqueado atende ao nível, libera
    for hero in manager.hero_manager.get_available_heroes():
        if hero.level >= min_level:
            return True
    return False

def check_not_active(quest, manager) -> bool:
    """Impede exibir quests que já estão em andamento."""
    return quest.id not in manager.active_quests


def process_expired_quests(manager):
    """Processa a lista inteira e move quests expiradas para failed."""
    expired = []
    for quest in manager.quests:
        if quest.id in manager.active_quests or \
           quest.id in manager.completed_quests or \
           quest.id in manager.failed_quests:
            continue

        if quest.is_expired(manager.current_turn):
            manager.failed_quests.add(quest.id)
            expired.append(quest)
            manager._log(manager.lm.t("quest_expired").format(quest=quest.name))

    if expired:
        names = [q.name for q in expired]
        manager.assistant.on_quests_expired(names)

def check_expired_quests(quest, manager):
    """Retorna False se a quest estiver expirada."""
    return not quest.is_expired(manager.current_turn)
