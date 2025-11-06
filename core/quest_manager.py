from core.hero_manager import HeroManager
from core.quest import Quest
from core.quest_success_calculator import calculate_success_chance, run_mission_roll
from core.save_manager import save_game, load_game
from core.assistant_manager import AssistantManager
from collections import defaultdict
from core.language_manager import LanguageManager
from core.quest_requirements import (
    check_required_quests,
    check_trigger_on_fail,
    check_not_completed,
    check_min_hero_level,
    check_not_active,
    check_expired_quests,
    check_available_turn,
    process_expired_quests,
)

# NOTE: agora QuestManager aceita um LanguageManager opcional para traduzir mensagens de log.


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
            check_available_turn,
            # adicionar outros futuramente
        ]

        # Language manager (opcional). Deve ter método t(key) -> str
        self.lm = LanguageManager()

        # HeroManager gerencia todos os heróis e desbloqueio
        self.hero_manager = HeroManager(language=self.lm.language)

        # Carrega quests
        self.quests = Quest.load_quests(language=self.lm.language)

        # Sets para progresso
        self.completed_quests = defaultdict(set)
        self.failed_quests = set()
        self.active_quests = {}  # dicionário: quest_id -> {"heroes": [...], "turns_left": n}
        self.current_turn = 1

        # Callback de log (injetado pelo GameplayScreen)
        self.log_callback = None

        # Callback de diálogo / UI
        self.dialog_callback = None
        self.ui_callback = None

        self.assistant = AssistantManager(self.lm)

    # -------------------- UI Log --------------------
    def set_log_callback(self, callback):
        """Registra função de log (ex: atualizar mission_log no Kivy)."""
        self.log_callback = callback

    def _log(self, message: str):
        """Envia mensagem para o log da UI, se existir."""
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
            msg = self.lm.t("quest_not_found").format(id=quest_id)
            return msg

        # Filtra heróis inválidos e pega os objetos
        selected_heroes = [self.get_hero(hid) for hid in hero_ids if self.get_hero(hid)]
        if not selected_heroes:
            return self.lm.t("no_valid_hero_selected")

        for hero in selected_heroes:
            hero.status = "on_mission"

        # Agenda a quest como "ativa" no dicionário
        self.active_quests[quest_id] = {
            "heroes": selected_heroes,
            "turns_left": quest.duration  # usa o campo duration do JSON
        }

        self._log(self.lm.t("heroes_sent").format(name=quest.name, turns=quest.duration))
        self._log(self.lm.t("heroes_list").format(list=", ".join(h.name for h in selected_heroes)))

        # Diálogo inicial, se existir callback
        if self.dialog_callback:
            self.dialog_callback(selected_heroes, quest.id, "start")

        if hasattr(self, "ui_callback") and self.ui_callback:
            self.ui_callback()

        return self.lm.t("mission_started")

    def resolve_quest(self, quest_id: int, data):
        self.pending_level_ups = []
        
        heroes = data["heroes"]
        quest = self.get_quest(quest_id)

        if quest is None:
            self._log(self.lm.t("quest_not_found_on_resolve").format(id=quest_id))
            return

        success_chance = calculate_success_chance(heroes, quest)
        result = run_mission_roll(success_chance)
        success_values = {"Sucesso", "Crítico", "Success", "Critical"}

        if result in success_values:
            xp_reward = quest.rewards.get("xp", 0)

            if quest.id not in self.completed_quests:
                self.completed_quests[quest.id] = set()

            for hero in heroes:
                # Guarda o nível antes de ganhar XP
                old_level = hero.level

                # Adiciona XP
                hero.add_xp(xp_reward)
                new_level = hero.level

                # Log do XP ganho
                self._log(self.lm.t("hero_gained_xp").format(hero=hero.name, xp=xp_reward))

                # 🔥 Se subiu de nível
                if new_level > old_level:
                    self._log(self.lm.t("hero_leveled_up").format(hero=hero.name, level=new_level))
                    self.pending_level_ups.append((hero.name, new_level))  # <<< guarda pra depois

                # Marca como completado
                self.completed_quests[quest.id].add(hero.id)

            self._log(self.lm.t("quest_completed").format(name=quest.name, result=result))
        else:
            self.failed_quests.add(quest.id)
            self._log(self.lm.t("quest_failed").format(name=quest.name))

        # Salva progresso
        save_game(self, self.save_file)

        # Mostra resumo
        self._log(self.lm.t("quest_summary_title").format(name=quest.name))
        self._log(self.lm.t("success_chance").format(pct=success_chance))
        self._log(self.lm.t("result_text").format(result=result))

        # Reseta status dos heróis
        for hero in heroes:
            try:
                hero.status = "idle"
            except Exception:
                pass

        # Callback de diálogo (resultado pós-quest)
        if self.dialog_callback:
            self.dialog_callback(heroes, quest.id, result)
            if self.assistant:
                for hero_name, level in self.pending_level_ups:
                    self.assistant.speak("assistant_level_up", hero=hero_name, level=level)

    # -------------------- Quests Disponíveis --------------------
    def available_quests(self):
        """Retorna lista de quests disponíveis (passando em todos os requisitos)."""
        # Primeiro, processa e remove quests expiradas antes de calcular as disponíveis
        process_expired_quests(self)

        quests_list = []
        new_quests = 0

        for q in self.quests:
            # Ignora se já estiver concluída, falhada ou ativa
            if q.id in self.completed_quests or q.id in self.failed_quests or q.id in self.active_quests:
                continue

            # Passa em todos os requisitos?
            if all(check(q, self) for check in self.requirement_checks):
                # Primeira vez que ficou disponível — registra o turno
                if getattr(q, "available_since_turn", None) is None:
                    q.available_since_turn = self.current_turn
                    new_quests += 1  # conta como nova quest liberada

                quests_list.append(q)

        # 🚨 Chama assistente se houver novas quests liberadas
        if new_quests > 0 and self.assistant:
            if self.assistant.dialogue_box:
                self.assistant.on_new_quests(new_quests)
            else:
                print(f"[Assistente] {new_quests} novas quests disponíveis!")

        return quests_list

    def get_active_quests(self):
        """Retorna objetos Quest ativos, não apenas IDs."""
        return [self.get_quest(qid) for qid in self.active_quests if self.get_quest(qid)]

    def get_available_quests(self):
        """Retorna as quests disponíveis (usa a lógica já existente)"""
        return self.available_quests()

    # dentro de core/quest_manager.py (método advance_turn)
    def advance_turn(self):
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
                self._log(self.lm.t("quest_not_found_on_resolve").format(id=qid))
                try:
                    del self.active_quests[qid]
                except KeyError:
                    pass
                continue

            # notifica que foi concluída (mensagem geral)
            self._log(self.lm.t("quest_auto_complete").format(name=quest.name))
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
        self._log(self.lm.t("quest_failed_timeout").format(name=quest.name))

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
