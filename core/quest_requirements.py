def check_available_turn(quest, manager) -> bool:
    """
    Verifica se a quest já está disponível de acordo com o turno atual.
    Se quest.available_from_turn não estiver definido, considera sempre disponível.
    """
    available_from_turn = getattr(quest, "available_from_turn", None)
    if available_from_turn is None:
        return True
    return manager.current_turn >= available_from_turn


def check_required_quests(quest, manager) -> bool:
    """
    Verifica se todas as quests obrigatórias foram concluídas,
    e se houver heróis obrigatórios, valida se eles participaram.
    """

    # --- Quests obrigatórias ---
    required_ids = getattr(quest, "required_quests", [])
    for req in required_ids:
        if req not in manager.completed_quests:
            return False  

    # --- Heróis obrigatórios ---
    required_heroes = getattr(quest, "required_heroes", [])
    if required_heroes:
        for req in required_ids:
            completed_by = manager.completed_quests.get(req, set())
            # Checa se pelo menos 1 dos required_heroes participou
            if not any(hid in completed_by for hid in required_heroes):
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


def check_expired_quests(quest, manager):
    """
    Processa a lista inteira e move quests que deveriam ter sido iniciadas para failed.
    """
    expired = []
    for quest in manager.quests:
        # Ignora se já está em andamento, completada ou falhada.
        if quest.id in manager.active_quests or \
           quest.id in manager.completed_quests or \
           quest.id in manager.failed_quests:
            continue

        if quest.is_expired(manager.current_turn):
            manager.failed_quests.add(quest.id)
            expired.append(quest)
            manager._log(manager.lm.t("quest_expired").format(quest=quest.name))
    return quest.id not in manager.active_quests
