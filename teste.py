# screens/gameplay/gameplay_screen.py
import customtkinter as ctk
from core.language_manager import LanguageManager
from core.dialogue_manager import DialogueManager
from screens.dialog_box import DialogueBox
from screens.gameplay.sidebar_panel import SidebarPanel
from screens.gameplay.quest_details_panel import QuestDetailsPanel
from screens.gameplay.log_panel import LogPanel
from screens.gameplay.pause_menu import PauseMenu
from screens.gameplay.turn_bar import TurnBar

class GameplayScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.qm = app.quest_manager
        self.lm = LanguageManager()
        self.dm = DialogueManager()
        self.dialog_box = DialogueBox(self.dm, self)
        self.qm.set_dialog_callback(self.open_dialog)
        self.qm.set_ui_callback(self.update_ui)
        self.qm.set_log_callback(self.update_log)

        self.build_ui()
        self.pause_menu = PauseMenu(self, app, self.lm, self.qm)
        self.bind("<Escape>", lambda e: self.pause_menu.open())

    def build_ui(self):
        """Monta o layout principal da tela"""
        # Layout em grid
        self.grid_columnconfigure(0, weight=3, minsize=500)
        self.grid_columnconfigure(1, weight=1, minsize=250)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=2)
        self.grid_rowconfigure(2, weight=1)

        # Linha 0: TurnBar (topo)
        self.turn_bar = TurnBar(
            self,
            self.qm,
            self.lm,
            on_advance=self.advance_turn,
            on_pause=self.open_pause_menu
        )
        self.turn_bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Linha 1: Quest details (esquerda)
        self.quest_details = QuestDetailsPanel(
            self,
            quest_manager=self.qm,
            language_manager=self.lm,
            on_start_quest=self.start_quest
        )
        self.quest_details.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=5)

        # Linha 1-2: Sidebar (direita)
        self.sidebar = SidebarPanel(
            self,
            language_manager=self.lm,
            on_quest_selected=self.show_quest_details
        )
        self.sidebar.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(2, 5), pady=5)

        # Linha 2: Log (esquerda inferior)
        self.log_panel = LogPanel(self, self.lm)
        self.log_panel.grid(row=2, column=0, sticky="nsew", padx=(5, 2), pady=(0, 5))

    def advance_turn(self):
        """Avança o turno e atualiza a interface."""
        self.qm.advance_turn()
        self.update_ui()
        self.turn_bar.update_turn()

    # --- Callbacks ---
    def show_quest_details(self, quest):
        self.quest_details.show(quest)

    def update_log(self, message):
        self.log_panel.update_log(message)

    def update_ui(self):
        self.sidebar.update_sidebar(self.qm)
        self.turn_label.configure(text=f"Turno: {self.qm.current_turn}")

    def start_quest(self, quest):
        self.qm.send_heroes_on_quest(quest.id, self.quest_details.get_selected_heroes(quest))
        self.update_ui()

    def open_dialog(self, heroes, quest, result):
        self.dialog_box.show_dialogue(heroes, quest, result)

    def open_pause_menu(self):
        """Abre o menu de pausa."""
        self.pause_menu.open()

    def update_ui(self):
        """Atualiza todos os componentes da tela."""
        self.sidebar.update_sidebar(self.qm)
        self.turn_bar.update_turn()
        self.update_log("---")

    def advance_turn(self):
        """Avança o turno e resolve missões pendentes."""
        self.qm.advance_turn()
        self.update_ui()
        self.turn_bar.update_turn()

    def start_quest(self, quest):
        """Chamado pelo QuestDetailsPanel ao clicar em 'Iniciar Missão'."""
        selected_heroes = self.quest_details.get_selected_heroes(quest)
        msg = self.qm.send_heroes_on_quest(quest.id, selected_heroes)
        if msg:
            self.update_log(msg)
        self.update_ui()

    def open_dialog(self, heroes, quest_id, result):
        """Abre diálogos (início ou fim de missões)."""
        quest = self.qm.get_quest(quest_id)
        if quest:
            self.dialog_box.show_dialogue(heroes, quest, result)

    def update_log(self, message: str):
        """Callback de log do QuestManager."""
        self.log_panel.update_log(message)

    def open_pause_menu(self):
        """Abre o menu de pausa."""
        self.pause_menu.open()
