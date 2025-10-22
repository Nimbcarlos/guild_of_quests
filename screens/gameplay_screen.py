from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import StringProperty
from functools import partial
from core.quest_success_calculator import calculate_success_chance
from core.dialogue_manager import DialogueManager
from core.language_manager import LanguageManager
from screens.dialog_box import DialogueBox
import core.save_manager as save
import re
from screens.gameplay.hero_popup import show_hero_details
from core.music_manager import get_music_manager


class GameplayScreen(Screen):
    active_quests_label = StringProperty()
    available_quests_label = StringProperty()
    completed_quests_label = StringProperty()
    log_messages = StringProperty()
    previous_screen = StringProperty("settings")
    first_time_entering = True  # Flag para primeira entrada
    
    def on_pre_enter(self):
        """Chamado ANTES de entrar na tela"""
        # Detecta se está vindo de settings
        self.coming_from_settings = (self.manager.current == "settings")

    def on_enter(self):
        self.qm = self.manager.quest_manager  
        self.lm = LanguageManager()
        self.pause_popup = None

        self.qm.hero_manager.check_hero_unlocks(self.qm.completed_quests, self.qm.current_turn)

        self.dm = DialogueManager()
        self.dialog_box = DialogueBox(self.dm)

    # 🚀 Atualiza o assistant já existente do QuestManager
        if self.qm.assistant:
            self.qm.assistant.dialogue_box = self.dialog_box

        self.qm.set_dialog_callback(self.open_dialog)
        self.qm.set_ui_callback(self.update_ui)
        
        self.active_quests_label = self.lm.t("active_quests")
        self.available_quests_label = self.lm.t("available_quests")
        self.completed_quests_label = self.lm.t("completed_quests")
        self.log_messages = self.lm.t("log_messages")

        if self.first_time_entering and not self.coming_from_settings:
            self.qm.assistant.on_game_start()
            self.first_time_entering = False

        self.update_sidebar()
        self.turn_bar()

        self.qm.set_log_callback(self.update_log)
        self.pending_assignments = {}  # { quest_id: [hero_ids] }
        # captura teclas
        Window.bind(on_key_down=self._on_key_down)
        self.ids.quest_details.clear_widgets()
        self.music = get_music_manager()
        self.music.play()           # Tocar

    def on_leave(self):
        # desliga o binding para evitar múltiplos binds ao voltar à tela
        try:
            Window.unbind(on_key_down=self._on_key_down)
        except Exception:
            pass

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 27:  # tecla ESC
            self.open_pause_menu()
            return True  # evita comportamento padrão (ex: fechar app no Android)
        return False

    def update_log(self, message):
        log_widget = self.ids.mission_log
        log_widget.add_widget(
            Label(
                text=message,
                size_hint_y=None,
                height=20,
                color=(0, 0, 0, 1)
            )
        )

        Clock.schedule_once(lambda dt: setattr(
        self.ids.mission_scroll, "scroll_y", 0
        ), 0.5)

    def turn_bar(self):
        # Verifica se o id existe no KV
        if "turn_log" not in self.ids:
            print("Aviso: id 'turn_log' não encontrado na tela. Certifique-se que o KV tem 'id: turn_log'.")
            return

        turn_widget = self.ids.turn_log
        turn_widget.clear_widgets()

        turn_label_text = self.lm.t("turn_label").format(turn=self.qm.current_turn)
        turn_widget.add_widget(
            Label(
                text=turn_label_text,
                size_hint_x=0.6,
                # size_hint_y=None,
                height=10,
                color=(0, 0, 0, 1)
            )
        )

        # Botão permanente de avançar turno (texto traduzido)
        turn_widget.add_widget(
            Button(
                text=self.lm.t("advance_turn_btn"),
                size_hint_x=0.4,
                # size_hint_y=None,
                height=40,
                on_release=lambda *_: self.advance_turn()
            )
        )

    def advance_turn(self, *_):
        # avança o turno no manager
        self.qm.advance_turn()

        # e se usar o ids.log_box:
        if "log_box" in self.ids:
            self.ids.log_box.add_widget(
                Label(
                    text=self.lm.t("turn_advanced").format(turn=self.qm.current_turn),
                    markup=False,
                    color=(0, 0, 0, 1),
                    size_hint_y=None,
                    height=20,
                )
            )

        # Atualiza UI que depende do estado do jogo
        self.update_sidebar()
        self.turn_bar()  # atualiza contador do turno


    def update_sidebar(self):
        qm = self.manager.quest_manager

        # Limpa listas
        self.ids.active_quests.clear_widgets()
        self.ids.available_quests.clear_widgets()
        self.ids.completed_quests.clear_widgets()

        self.lm.t("mission_log")

        for quest in qm.get_active_quests():
            self.ids.active_quests.add_widget(
                Button(
                    text=f'{quest.name} ({quest.type})',
                    size_hint_y=None,
                    height=40,
                    on_release=partial(self.show_active_quest_details, quest)
                )
            )

        for quest in qm.get_available_quests():
            self.ids.available_quests.add_widget(
                Button(
                    text=f"{quest.name} ({quest.type})",
                    size_hint_y=None,
                    height=40,
                    on_release=partial(self.show_quest_details, quest)
                )
            )

        self.ids.completed_quests.clear_widgets()
        self.ids.completed_quests.add_widget(
            Button(
                text=self.lm.t("completed_quests_title"),
                size_hint_y=None,
                height=40,
                on_release=self.show_completed_quests_popup
            )
        )

    def show_quest_details(self, quest, *_):
        """Mostra painel com detalhes da quest e opções de heróis."""
        container = self.ids.quest_details
        container.clear_widgets()

        self.pending_assignments[quest.id] = []

        self.qm.hero_manager.check_hero_unlocks(self.qm.completed_quests, self.qm.current_turn)

        # Lista os heróis disponíveis
        available_heroes = self.qm.hero_manager.get_available_heroes()

        container.add_widget(Label(
            text=f"[b]{quest.name}[/b]",
            markup=True, font_size=24, color=(0, 0, 0, 1),
            size_hint_y=None, height=30
        ))

        container.add_widget(Label(
            text=f"{self.lm.t('type_label')}: {quest.type} | {self.lm.t('difficulty_label')}: {quest.difficulty}",
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=20
        ))

        # Taxa de sucesso
        self.success_label = Label(
            text=f'{self.lm.t('success_rate')}: --',
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=25
        )
        container.add_widget(self.success_label)

        desc_label = Label(
            text=quest.description,
            color=(0, 0, 0, 1),
            halign="left",
            text_size=(container.width * 0.9, None),
            valign="top",
            size_hint_y=None,
            font_size=15
        )
        desc_label.bind(
            texture_size=lambda *x: desc_label.setter("height")(desc_label, desc_label.texture_size[1])
        )
        container.add_widget(desc_label)

        # "Heróis disponíveis:"
        container.add_widget(Label(
            text=self.lm.t("available_heroes"),
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=25
        ))

        heroes_box = BoxLayout(orientation="vertical", size_hint_y=None)
        heroes_box.bind(minimum_height=heroes_box.setter("height"))
        available_heroes = self.qm.hero_manager.get_available_heroes()

        for hero in available_heroes:

            row = BoxLayout(size_hint_y=None, height=40, spacing=10)

            # Foto do herói (assumindo que hero.photo é o caminho da imagem)
            if getattr(hero, "photo_url", None):
                row.add_widget(Image(
                    source=hero.photo_url,
                    size_hint_x=None,
                    width=50
                ))
            else:
                row.add_widget(Label(
                    text="❓",
                    size_hint_x=None,
                    width=50
                ))

            # Nome permanece
            row.add_widget(Label(
                text=hero.name,
                color=(0, 0, 0, 1),
                halign="left",
                valign="middle"
            ))

            # Classe (traduz rótulo "Classe")
            row.add_widget(Label(
                text=f"{self.lm.t('class')}: {getattr(hero, 'hero_class', 'Unknown')}",
                color=(0, 0, 0, 1),
                halign="left",
                valign="middle"
            ))

            # Level — CORREÇÃO: use o atributo 'level' do hero, não a tradução como nome de atributo
            row.add_widget(Label(
                text=f"{self.lm.t('lvl_prefix')} {getattr(hero, 'level', 1)}",
                color=(0, 0, 0, 1),
                halign="left",
                valign="middle"
            ))


            # Botão de detalhes
            row.add_widget(Button(
                text="🔍",
                size_hint_x=None,
                width=50,
                on_release=lambda *_, h=hero: show_hero_details(self, h)
            ))

            # --- Botão de seleção com feedback visual ---
            select_btn = Button(
                text=self.lm.t('select'),
                size_hint_x=None,
                width=120,
                background_color=(0.8, 0.8, 0.8, 1)  # cinza claro (não selecionado)
            )

            def on_select_press(btn, h=hero):
                """Chama a função original e alterna o visual."""
                self.select_hero_for_quest(quest, h)

                quest_id = quest.id
                if h.id in self.pending_assignments.get(quest_id, []):
                    # Está selecionado → destacar
                    btn.text = self.lm.t('selected')
                    btn.background_color = (0.4, 0.8, 0.4, 1)  # verde
                else:
                    # Foi removido → voltar ao normal
                    btn.text = self.lm.t('select')
                    btn.background_color = (0.8, 0.8, 0.8, 1)  # cinza

            select_btn.bind(on_release=on_select_press)
            row.add_widget(select_btn)

            heroes_box.add_widget(row)

        scroll = ScrollView(size_hint_y=0.4)
        scroll.add_widget(heroes_box)
        container.add_widget(scroll)

        # Botão enviar
        container.add_widget(Button(
            text=self.lm.t("send_to_quest_btn"),
            size_hint_y=None,
            height=50,
            on_release=lambda *_: self.start_quest(quest)
        ))

    def show_active_quest_details(self, quest, *_):
        """Mostra painel de detalhes de uma quest ativa — heróis designados e turnos restantes."""
        container = self.ids.quest_details
        container.clear_widgets()

        quest_data = self.qm.active_quests.get(quest.id)
        if not quest_data:
            container.add_widget(Label(
                text=self.lm.t("quest_not_found"),
                color=(0, 0, 0, 1)
            ))
            return

        heroes = quest_data.get("heroes", [])
        turns_left = quest_data.get("turns_left", "?")

        # Cabeçalho
        container.add_widget(Label(
            text=f"[b]{quest.name}[/b]",
            markup=True,
            font_size=24,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=30
        ))

        # Tipo / Dificuldade / Turnos restantes
        container.add_widget(Label(
            text=f"{self.lm.t('type_label')}: {quest.type} | "
                f"{self.lm.t('difficulty_label')}: {quest.difficulty} | "
                f"{self.lm.t('turns_left_label')}: {turns_left}",
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=25
        ))

        container.add_widget(Label(
            text=quest.description,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=60
        ))

        # Lista de heróis na missão
        container.add_widget(Label(
            text=self.lm.t("heroes_on_quest"),
            bold=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=25
        ))

        heroes_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=5, padding=[5, 0])
        heroes_box.bind(minimum_height=heroes_box.setter("height"))

        for hero in heroes:
            row = BoxLayout(size_hint_y=None, height=60, spacing=10)

            # Foto do herói
            if getattr(hero, "photo_url", None):
                row.add_widget(Image(
                    source=hero.photo_url,
                    size_hint_x=None,
                    width=50
                ))
            else:
                row.add_widget(Label(
                    text="❓",
                    size_hint_x=None,
                    width=50
                ))

            # Nome e classe
            row.add_widget(Label(
                text=f"[b]{hero.name}[/b]\n{self.lm.t('class')}: {getattr(hero, 'hero_class', 'Unknown')} | "
                    f"{self.lm.t('lvl_prefix')} {getattr(hero, 'level', 1)}",
                markup=True,
                halign="left",
                valign="middle",
                color=(0, 0, 0, 1)
            ))

            # Botão de detalhes do herói
            row.add_widget(Button(
                text="[font=Icons]\uf005[/font]",
                size_hint_x=None,
                width=50,
                on_release=lambda *_, h=hero: show_hero_details(self, h)
            ))

            heroes_box.add_widget(row)

        scroll = ScrollView(size_hint_y=0.4)
        scroll.add_widget(heroes_box)
        container.add_widget(scroll)

        # Botão de voltar/fechar
        container.add_widget(Button(
            text=self.lm.t("close"),
            size_hint_y=None,
            height=45,
            on_release=lambda *_: container.clear_widgets()
        ))

    def select_hero_for_quest(self, quest, hero):
        """Adiciona ou remove um herói da seleção dessa quest."""
        if quest.id not in self.pending_assignments:
            self.pending_assignments[quest.id] = []

        if hero.id in self.pending_assignments[quest.id]:
            # já estava selecionado → desmarca
            self.pending_assignments[quest.id].remove(hero.id)
        else:
            # adiciona
            self.pending_assignments[quest.id].append(hero.id)
        self.update_success_label(quest)

    def confirm_quest_assignment(self, quest):
        """Confirma e envia os heróis selecionados para a quest."""
        hero_ids = self.pending_assignments.get(quest.id, [])
        if not hero_ids:
            self.qm._log(self.lm.t("no_hero_selected"))
            return

        self.qm.send_heroes_on_quest(quest.id, hero_ids)
        # limpa seleção dessa quest
        self.pending_assignments.pop(quest.id, None)

    def start_quest(self, quest):
        """Envia os heróis selecionados para uma quest específica e mostra o diálogo inicial."""
        hero_ids = self.pending_assignments.get(quest.id, [])
        if not hero_ids:
            self.qm._log("⚠️ Nenhum herói selecionado para esta missão.")
            return

        # Pega os objetos dos heróis selecionados
        heroes = [self.qm.get_hero(hid) for hid in hero_ids if self.qm.get_hero(hid)]

        # 🔹 Mostra diálogo inicial antes de enviar (usa o DialogueBox)
        # use "start" para disparar o fluxo adequado dentro do DialogueBox/DialogueManager
        # if heroes:
        #     try:
        #         # DialogueBox.show_dialogue trata result == "start" como diálogo inicial
        #         self.dialog_box.show_dialogue(heroes, quest.id, "start", parent_size=self.size)
        #     except Exception as e:
        #         # fallback silencioso em caso de algo errado no diálogo
        #         print("Erro ao abrir diálogo inicial:", e)

        # 🔹 Chama o QuestManager para registrar a missão
        self.qm.send_heroes_on_quest(quest.id, hero_ids)

        # 🔹 Limpa a seleção dessa quest (já enviada)
        self.pending_assignments.pop(quest.id, None)

        # 🔹 Limpa/atualiza a UI relacionada (painel de detalhes, sidebar, turnbar)
        # limpar o painel de detalhes é importante para não mostrar controles obsoletos
        try:
            self.ids.quest_details.clear_widgets()
        except Exception:
            # se o id não existir ou erro qualquer, apenas passa
            pass

        # Atualiza as listas (active/available/completed) e o contador de turno
        self.update_sidebar()
        self.turn_bar()

        # Fecha popups/diálogos abertos do DialogueBox, se desejar
        # (não fecha o diálogo inicial que acabamos de abrir — a menos que queira)
        # self.clear_ui()  # opcional — descomente se quiser fechar tudo aqui


    def clear_ui(self):
        """Limpeza geral da UI do gameplay (fechar popups, limpar painéis, limpar seleção)."""

        # 1) Limpa painel de detalhes (onde ficou a lista de heróis)
        try:
            if "quest_details" in self.ids:
                self.ids.quest_details.clear_widgets()
        except Exception:
            pass

        # 2) Limpa seleção pendente (todas)
        try:
            self.pending_assignments = {}
        except Exception:
            self.pending_assignments = {}

        # 3) Fecha popups que a tela pode ter criado
        # popup de pausa / save
        for attr in ("pause_popup", "save_popup", "current_popup"):
            popup = getattr(self, attr, None)
            if popup:
                try:
                    popup.dismiss()
                except Exception:
                    pass
                try:
                    setattr(self, attr, None)
                except Exception:
                    pass

        # 4) Fecha popup do DialogueBox (se aberto) — só se você quiser forçar fechar
        try:
            if getattr(self, "dialog_box", None) and getattr(self.dialog_box, "popup", None):
                try:
                    self.dialog_box.popup.dismiss()
                except Exception:
                    pass
                self.dialog_box.popup = None
        except Exception:
            pass

        # 5) Atualiza sidebar / turn_bar para refletir o estado atual (ex.: nova active_quests)
        try:
            self.update_sidebar()
        except Exception:
            pass
        try:
            self.turn_bar()
        except Exception:
            pass

        # debug
        print("🧹 GameplayScreen: UI limpa (clear_ui).")

    def update_success_label(self, quest):
        """Atualiza a taxa de sucesso no label quando heróis são selecionados."""
        hero_ids = self.pending_assignments.get(quest.id, [])
        heroes = [self.qm.get_hero(hid) for hid in hero_ids if self.qm.get_hero(hid)]

        if not heroes:
            self.success_label.text = f"{self.lm.t('success_rate')}: --%"
            return

        chance = calculate_success_chance(heroes, quest)
        self.success_label.text = f"{self.lm.t("success_rate")}: {chance*100:.0f}%"

    def open_pause_menu(self):
        if self.pause_popup and self.pause_popup.parent:
            self.pause_popup.dismiss()
            self.pause_popup = None
            return

        content = BoxLayout(orientation="vertical", spacing=10, padding=10)

        btn_save = Button(text=self.lm.t("save_game"), size_hint_y=None, height=48)
        btn_save.bind(on_release=self.save_and_close_popup)
        content.add_widget(btn_save)

        btn_load = Button(text=self.lm.t("load_game"), size_hint_y=None, height=48)
        btn_load.bind(on_release=self.load_and_close_popup)
        content.add_widget(btn_load)

        btn_settings = Button(text=self.lm.t("settings_title"), size_hint_y=None, height=48)
        btn_settings.bind(on_release=self.open_settings)
        content.add_widget(btn_settings)

        btn_menu = Button(text=self.lm.t("back_to_menu"), size_hint_y=None, height=48)
        btn_menu.bind(on_release=self.goto_menu)
        content.add_widget(btn_menu)

        btn_quit = Button(text=self.lm.t("quit_game"), size_hint_y=None, height=48)
        btn_quit.bind(on_release=lambda *_: App.get_running_app().stop())
        content.add_widget(btn_quit)

        # guarda no self para poder dar .dismiss() depois
        self.pause_popup = Popup(title=self.lm.t("pause_menu_title"),
                                content=content, 
                                size_hint=(None, None),
                                size=(300, 360)
                                )
        self.pause_popup.open()

    def save_and_close_popup(self, *args):
        # Fecha o popup de pausa, se existir
        if getattr(self, "pause_popup", None):
            try:
                self.pause_popup.dismiss()
            except Exception:
                pass
            self.pause_popup = None

        # Popup reduzido e simples
        box = BoxLayout(orientation="vertical", spacing=5, padding=10)

        input_name = TextInput(
            hint_text=self.lm.t("save_name_hint"),
            multiline=False,
            size_hint_y=None,
            height=40,
            input_filter=self.safe_input_filter  # 🔹 permite só caracteres válidos
        )
        box.add_widget(input_name)

        btns = BoxLayout(size_hint_y=None, height=35, spacing=5)
        btns.add_widget(Button(text=self.lm.t("save"),
                               on_release=lambda *_: self.confirm_save(input_name.text)))
        btns.add_widget(Button(text=self.lm.t("cancel"),
                               on_release=lambda *_: popup.dismiss()))
        box.add_widget(btns)

        popup = Popup(
            title=self.lm.t("save_game"),
            content=box,
            size_hint=(0.5, 0.3),  # 🔹 menor que antes
            auto_dismiss=False
        )
        popup.open()
        self.save_popup = popup

    def confirm_save(self, filename):
        # 🔹 Apenas letras, números e underscore
        if not re.match(r"^[A-Za-z0-9_]+$", filename):
            self.qm._log(self.lm.t("invalid_name"))
            return

        filename = f"{filename}.json"

        qm = self.manager.quest_manager
        save.save_game(qm, filename)

        qm._log(self.lm.t("game_saved").format(filename=filename))

        # Fecha o popup
        if getattr(self, "save_popup", None):
            try:
                self.save_popup.dismiss()
            except Exception:
                pass
            self.save_popup = None

    def load_and_close_popup(self, *args):
        if self.pause_popup:
            self.pause_popup.dismiss()
            self.pause_popup = None
        
        elif getattr(self, "pause_popup", None):
            try:
                self.pause_popup.dismiss()
            except Exception:
                pass
            self.pause_popup = None

        load_screen = self.manager.get_screen("loadgame")
        load_screen.previous_screen = "gameplay"
        self.manager.current = "loadgame"

    def open_settings(self, *args):
        if getattr(self, "pause_popup", None):
            try:
                self.pause_popup.dismiss()
                self.music.stop()
            except Exception:
                pass
            self.pause_popup = None

        settings = self.manager.get_screen("settings")
        settings.previous_screen = "gameplay"
        self.manager.current = "settings"

    def goto_menu(self, *args):
        # fecha popup se necessário
        if getattr(self, "pause_popup", None):
            try:
                self.pause_popup.dismiss()
                self.music.stop()
            except Exception:
                pass
            self.pause_popup = None

        # volta ao menu principal
        self.manager.current = "menu"

    def open_dialog(self, selected_heroes, quest, result):
        # Aqui você só chama a função passando heróis, quest_id e resultado
        self.dialog_box.show_dialogue(selected_heroes, quest, result, parent_size=self.size)

    @staticmethod
    def safe_input_filter(substring, from_undo):
        # Permite apenas letras, números e underline
        return re.sub(r'[^A-Za-z0-9_]', '', substring)

    def advance_turn(self):
        self.qm.advance_turn()
        # atualiza o texto do widget fixo
        self.qm._log(self.lm.t("turn_advanced").format(turn=self.qm.current_turn))
        self.update_sidebar()
        self.turn_bar()


    def update_ui(self):
        """Atualiza todas as partes visuais ligadas ao estado do jogo."""
        self.update_sidebar()
        self.turn_bar()

    def show_assistant_message(self, msg: str):
        """Repassa a fala da assistente para o DialogueBox"""
        if hasattr(self, "dialog_box"):
            self.dialog_box.show_assistant_message(msg)
        else:
            print(f"[Assistente] {msg} (sem DialogueBox ativo)")

    def show_completed_quests_popup(self, *_):
        """Abre um popup listando as quests completas e permite ver detalhes."""
        qm = self.qm

        # === Popup principal ===
        main_layout = BoxLayout(orientation="horizontal", spacing=15, padding=15)

        # === LISTA LATERAL (esquerda) ===
        quest_list_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=5)
        quest_list_box.bind(minimum_height=quest_list_box.setter('height'))
        
        quest_scroll = ScrollView(size_hint=(0.35, 1))
        quest_scroll.add_widget(quest_list_box)

        # === ÁREA DE DETALHES (direita) ===
        details_container = BoxLayout(orientation="vertical", spacing=10)
        
        # Título da quest selecionada (topo)
        quest_title_label = Label(
            text="",
            color=(0, 0, 0, 1),
            font_size=24,
            bold=True,
            markup=True,
            halign="left",
            valign="top",
            size_hint_y=None,
            height=60
        )
        quest_title_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        
        # ScrollView para a descrição (caso seja longa)
        details_scroll = ScrollView(size_hint=(1, 1))
        
        details_label = Label(
            text=self.lm.t("select_quest_to_view"),
            color=(0, 0, 0, 1),
            font_size=16,
            halign="left",
            valign="top",
            size_hint_y=None
        )
        details_label.bind(
            texture_size=lambda instance, value: setattr(instance, 'height', value[1])
        )
        details_label.bind(
            size=lambda instance, value: setattr(instance, 'text_size', (value[0] - 20, None))
        )
        
        details_scroll.add_widget(details_label)
        
        # Adiciona título e scroll ao container
        details_container.add_widget(quest_title_label)
        details_container.add_widget(details_scroll)

        main_layout.add_widget(quest_scroll)
        main_layout.add_widget(details_container)

        # === Função interna para atualizar detalhes ===
        def show_details(quest):
            # Atualiza o título
            quest_title_label.text = f"[b]{quest.name}[/b]"
            
            # Pega os heróis que completaram essa quest
            hero_ids = qm.completed_quests.get(quest.id, set())
            
            # Monta a lista de nomes dos heróis
            hero_names = []
            if hero_ids:
                for hero_id in hero_ids:
                    hero = self.qm.hero_manager.get_hero_by_id(hero_id)
                    if hero:
                        hero_names.append(hero.name)
            
            # Formata o texto dos heróis
            if hero_names:
                heroes_text = f"[b]{self.lm.t('completed_by')}:[/b] {', '.join(hero_names)}\n\n"
            else:
                heroes_text = ""
            
            # Atualiza os detalhes
            details_label.text = (
                f"[b]{self.lm.t('type_label')}:[/b] {quest.type}\n"
                f"[b]{self.lm.t('difficulty_label')}:[/b] {quest.difficulty}\n\n"
                f"{heroes_text}"
                f"{quest.description}"
            )
            details_label.markup = True

        # === Preenche a lista de quests ===
        completed = qm.completed_quests
        if not completed:
            quest_list_box.add_widget(Label(
                text=self.lm.t("no_completed_quests"),
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=30
            ))
        else:
            for qid in completed:
                q = qm.get_quest(qid)
                if q:
                    btn = Button(
                        text=q.name,
                        size_hint_y=None,
                        height=50,
                        background_color=(0.9, 0.85, 0.7, 1),
                        color=(0, 0, 0, 1),
                        on_release=lambda *_, quest=q: show_details(quest)
                    )
                    quest_list_box.add_widget(btn)

        # === Cria o popup ===
        popup = Popup(
            title=self.lm.t("completed_quests_title"),
            content=main_layout,
            size_hint=(None, None),
            size=(500, 500),
            auto_dismiss=True,
            background="assets/background.png",
            separator_color=(0, 0, 0, 0)
        )
        popup.open()
