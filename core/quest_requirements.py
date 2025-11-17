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
    required_quests = getattr(quest, "required_quests", [])
    required_heroes = getattr(quest, "required_heroes", [])
    forbidden_heroes = getattr(quest, "forbidden_heroes", [])

    # 1 — Verifica se todas as required_quests foram concluídas
    for req in required_quests:
        if req not in manager.completed_quests:
            return False
    
    # 2 — Verifica se os heróis obrigatórios participaram
    if required_heroes:
        for req in required_quests:
            completed_by = manager.completed_quests.get(req, set())
            
            # Verifica cada requisito de herói
            for hero_req in required_heroes:
                
                # Converte int para string se necessário
                hero_req_str = str(hero_req)
                
                # Se tem "_", significa que TODOS devem ter participado
                if '_' in hero_req_str:
                    hero_ids = [int(h.strip()) for h in hero_req_str.split('_')]
                    if not all(hero_id in completed_by for hero_id in hero_ids):
                        return False
                
                # Requisito simples: herói específico deve estar presente
                else:
                    hero_id = int(hero_req_str)
                    if hero_id not in completed_by:
                        return False
    
    # 3 — Verifica se algum herói proibido participou
    if forbidden_heroes:
        for req in required_quests:
            completed_by = manager.completed_quests.get(req, set())
            
            # Se QUALQUER herói proibido completou, bloqueia a quest
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
