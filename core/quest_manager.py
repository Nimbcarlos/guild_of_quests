from core.hero_manager import HeroManager
from core.quest import Quest
from core.quest_success_calculator import calculate_success_chance, run_mission_roll
from core.save_manager import save_game, load_game
from core.quest_requirements import (
    check_required_quests,
    check_trigger_on_fail,
    check_not_completed,
    check_min_hero_level,
    check_not_active,
    check_expired_quests,
)

class QuestManager:
    def __init__(self, save_file="auto_save.json"):
        self.save_file = save_file
        self.requirement_checks = [
            check_not_completed,
            check_trigger_on_fail,
            check_required_quests,
            check_min_hero_level,
            check_not_active,
            check_expired_quests,
            # adicionar outros futuramente
        ]

        # HeroManager gerencia todos os heróis e desbloqueio
        self.hero_manager = HeroManager()

        # Carrega quests
        self.quests = Quest.load_quests()

        # Sets para progresso
        self.completed_quests = set()
        self.failed_quests = set()
        self.active_quests = {}  # Corrigido para ser um dicionário
        self.current_turn = 1

        # Callback de log (injetado pelo GameplayScreen)
        self.log_callback = None

    # -------------------- UI Log --------------------
    def set_log_callback(self, callback):
        """Registra função de log (ex: atualizar mission_log no Kivy)."""
        self.log_callback = callback

    def _log(self, message: str):
        """Envia mensagem para o log da UI, se existir."""
        print(message)  # mantém no console também
        if self.log_callback:
            self.log_callback(message)

    def set_dialog_callback(self, callback):
        """Registra função de diálogo (ex: abrir DialogueBox no Kivy)."""
        self.dialog_callback = callback

    # -------------------- Heróis --------------------
    def get_hero(self, hero_id: str):
        """Retorna o herói pelo ID via HeroManager"""
        return self.hero_manager.get_hero_by_id(hero_id)

    # -------------------- Quests --------------------
    def get_quest(self, quest_id: str):
        """Retorna a quest pelo ID"""
        for quest in self.quests:
            if quest.id == quest_id:
                return quest
        return None

    def send_heroes_on_quest(self, quest_id: int, hero_ids: list[str]):
        """
        Envia heróis para a quest e agenda sua conclusão após os turnos.
        """
        quest = self.get_quest(quest_id)
        if not quest:
            return f"⚠️ Quest com ID '{quest_id}' não encontrada!"

        # Filtra heróis inválidos e pega os objetos
        selected_heroes = [self.get_hero(hid) for hid in hero_ids if self.get_hero(hid)]
        if not selected_heroes:
            return "Nenhum herói válido foi selecionado."

        for hero in selected_heroes:
            hero.status = "on_mission"

        # 🔹 Agenda a quest como "ativa" no dicionário
        self.active_quests[quest_id] = {
            "heroes": selected_heroes,
            "turns_left": quest.duration  # usa o campo duration do JSON
        }

        self._log(f"🚀 Heróis enviados para '{quest.name}' ({quest.duration} turnos restantes).")
        self._log(f"👥 {', '.join(h.name for h in selected_heroes)}")

        # 🔹 Aqui entraria o diálogo inicial, se quiser
        if self.dialog_callback:
            self.dialog_callback(selected_heroes, quest.id, "start")

        if hasattr(self, "ui_callback") and self.ui_callback:
            self.ui_callback()

        return "Missão iniciada!"

    def resolve_quest(self, quest_id: int, data: dict):
        """
        Conclui a missão após os turnos terminarem.
        """
        heroes = data["heroes"]
        quest = self.get_quest(quest_id)

        success_chance = calculate_success_chance(heroes, quest)
        result = run_mission_roll(success_chance)

        if result in ["Sucesso", "Crítico"]:
            xp_reward = quest.rewards.get("xp", 0)
            for hero in heroes:
                hero.add_xp(xp_reward)
                self._log(f"✅ {hero.name} ganhou {xp_reward} XP!")
            self.completed_quests.add(quest.id)
            self._log(f"🏆 Quest '{quest.name}' concluída com {result}!")
        else:
            self.failed_quests.add(quest.id)
            self._log(f"❌ Quest '{quest.name}' falhou!")

        # Salva progresso
        save_game(self, self.save_file)

        # Mostra resumo
        self._log(f"📜 Quest: {quest.name}")
        self._log(f"🎯 Chance de sucesso: {success_chance:.0%}")
        self._log(f"🎲 Resultado: {result}")

        for hero in data["heroes"]:
            # Se quiser lógica de ferimento ou descanso
            hero.status = "idle"

        if self.dialog_callback:
            self.dialog_callback(heroes, quest.id, result)

    # -------------------- Quests Disponíveis --------------------
    def available_quests(self):
        """Retorna lista de quests disponíveis (passando em todos os requisitos)."""
        quests_list = []
        for q in self.quests:

            if q.id in self.completed_quests or q.id in self.failed_quests or q.id in self.active_quests:
                continue

            if all(check(q, self) for check in self.requirement_checks):

                if q.available_since_turn is None:
                    q.available_since_turn = self.current_turn
                quests_list.append(q)
        return quests_list

    def get_active_quests(self):
        """Retorna objetos Quest ativos, não apenas IDs."""
        return [self.get_quest(qid) for qid in self.active_quests if self.get_quest(qid)]

    def get_available_quests(self):
        """Retorna as quests disponíveis (usa a lógica já existente)"""
        return self.available_quests()

    # dentro de core/quest_manager.py (método advance_turn)
    def advance_turn(self):
        print(f"Avançando para o turno {self.current_turn + 1}")
        self.current_turn += 1

        # coleciona quests que precisam ser resolvidas (evita modificar dict durante iteração)
        to_resolve = []
        for qid, data in list(self.active_quests.items()):
            # decrementa
            data["turns_left"] = data.get("turns_left", 0) - 1
            # se chegou a zero, agenda resolução
            if data["turns_left"] <= 0:
                to_resolve.append((qid, data))

        # resolve separadamente
        for qid, data in to_resolve:
            quest = self.get_quest(qid)
            if quest is None:
                # quest não existe no catálogo atual: remove e loga
                self._log(f"⚠️ Quest com id '{qid}' não encontrada ao resolver (removendo do ativo).")
                try:
                    del self.active_quests[qid]
                except KeyError:
                    pass
                continue

            self._log(f"Quest {quest.name} foi concluída!")
            # chama sua função que aplica XP e marca completada/falhada
            self.resolve_quest(qid, data)
            # remove da lista de ativas
            try:
                del self.active_quests[qid]
            except KeyError:
                pass

    def fail_quest(self, quest_id):
        quest = self.get_quest(quest_id)
        if not quest:
            return
        self.failed_quests.add(quest_id)
        if quest_id in self.active_quests:
            del self.active_quests[quest_id]
        self._log(f"⌛ Quest '{quest.name}' falhou por tempo esgotado!")

    def set_ui_callback(self, callback):
        self.ui_callback = callback

    def reset_game_state(self):
        self.current_turn = 1
        self.active_quests = {}
        self.completed_quests = set()
        self.failed_quests = set()

        # zera o estado das quests
        for quest in self.quests:
            quest.available_since_turn = None
