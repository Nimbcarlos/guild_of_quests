# screens/gameplay/gameplay_screen.py - Refatorado
import customtkinter as ctk
from tkinter import messagebox
import re
from core.dialogue_manager import DialogueManager
from core.language_manager import LanguageManager
from screens.dialog_box import DialogueBox
import core.save_manager as save

# Importa os painéis modularizados
from screens.gameplay.sidebar_panel import SidebarPanel
from screens.gameplay.quest_details_panel import QuestDetailsPanel
from screens.gameplay.log_panel import LogPanel
from screens.gameplay.pause_menu import PauseMenu


class GameplayScreen(ctk.CTkFrame):
    """Tela principal de gameplay - coordena todos os painéis"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.qm = app.quest_manager
        self.lm = LanguageManager()
        
        # Dialog e Assistant
        self.dm = DialogueManager()
        self.dialog_box = DialogueBox(self.dm, self)
        
        if self.qm.assistant:
            self.qm.assistant.dialogue_box = self.dialog_box
        
        self.qm.set_dialog_callback(self.open_dialog)
        self.qm.set_ui_callback(self.update_ui)
        self.qm.set_log_callback(self.log_message)
        
        # Overlays (para garantir que só existe um de cada vez)
        self.pause_overlay = None
        self.save_overlay = None
        self.hero_overlay = None
        
        # Build UI
        self.build_ui()
        
        # Bind ESC key
        self.bind("<Escape>", lambda e: self.toggle_pause_menu())
    
    def on_show(self):
        """Callback quando a tela é mostrada"""
        self.qm.hero_manager.check_hero_unlocks(
            self.qm.completed_quests, 
            self.qm.current_turn
        )
        self.qm.assistant.on_game_start()
        self.update_ui()
    
    def build_ui(self):
        """Constrói a interface principal"""
        # Configura grid
        self.grid_columnconfigure(0, weight=3, minsize=500)  # Esquerda
        self.grid_columnconfigure(1, weight=1, minsize=250)  # Direita
        self.grid_rowconfigure(0, weight=0)  # Turn bar
        self.grid_rowconfigure(1, weight=2)  # Quest Details
        self.grid_rowconfigure(2, weight=1)  # Log
        
        # ==================== TURN BAR ====================
        self.turn_frame = ctk.CTkFrame(self, height=50)
        self.turn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        self.turn_label = ctk.CTkLabel(
            self.turn_frame,
            text=f"Turno: {self.qm.current_turn}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.turn_label.pack(side="left", padx=20)
        
        advance_btn = ctk.CTkButton(
            self.turn_frame,
            text=self.lm.t("advance_turn_btn"),
            command=self.advance_turn,
            width=150
        )
        advance_btn.pack(side="right", padx=20)
     
        # ==================== QUEST DETAILS PANEL ====================
        quest_container = ctk.CTkFrame(self)
        quest_container.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=5)
        
        self.quest_details_panel = QuestDetailsPanel(
            quest_container,
            self.lm,
            self.qm,
            self.show_hero_details
        )
        self.quest_details_panel.pack(fill="both", expand=True)
        
        # Conecta o callback de start quest
        self.quest_details_panel.on_start_quest = self.start_quest
        
        # ==================== SIDEBAR PANEL ====================
        self.sidebar_panel = SidebarPanel(
            self,
            self.lm,
            self.quest_details_panel.show_quest
        )
        self.sidebar_panel.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(2, 5), pady=5)
        
        # ==================== LOG PANEL ====================
        log_container = ctk.CTkFrame(self)
        log_container.grid(row=2, column=0, sticky="nsew", padx=(5, 2), pady=(0, 5))
        
        self.log_panel = LogPanel(log_container, self.lm)
        self.log_panel.pack(fill="both", expand=True)
        
        # ==================== PAUSE MENU (instância) ====================
        self.pause_menu = PauseMenu(self, self.lm, self.app)
    
    # ==================== UI UPDATES ====================
    def update_turn_bar(self):
        """Atualiza o contador de turno"""
        self.turn_label.configure(
            text=f"{self.lm.t('turn_label').format(turn=self.qm.current_turn)}"
        )
    
    def log_message(self, message):
        """Adiciona mensagem ao log"""
        self.log_panel.add_message(message)
    
    def update_ui(self):
        """Atualiza toda a UI"""
        self.sidebar_panel.update(self.qm)
        self.update_turn_bar()
    
    # ==================== QUEST FLOW ====================
    def start_quest(self, quest, heroes):
        """Envia heróis para a quest"""
        # Mostra diálogo inicial
        try:
            self.dialog_box.show_dialogue(heroes, quest.id, "start")
        except Exception as e:
            print(f"Erro ao abrir diálogo inicial: {e}")
        
        # Envia para quest
        hero_ids = [h.id for h in heroes]
        self.qm.send_heroes_on_quest(quest.id, hero_ids)
        
        # Limpa seleção
        self.quest_details_panel.pending_assignments.pop(quest.id, None)
        self.quest_details_panel.clear()
        
        # Atualiza UI
        self.update_ui()
    
    def advance_turn(self):
        """Avança o turno"""
        self.qm.advance_turn()
        self.qm._log(self.lm.t("turn_advanced").format(turn=self.qm.current_turn))
        self.update_ui()
    
    def open_dialog(self, selected_heroes, quest, result):
        """Callback para abrir diálogo"""
        self.dialog_box.show_dialogue(selected_heroes, quest, result)
    
    # ==================== PAUSE MENU ====================
    def toggle_pause_menu(self):
        """Abre/fecha o menu de pausa"""
        self.pause_menu.show(on_save_callback=self.save_game_dialog)
    
    # ==================== SAVE DIALOG ====================
    def save_game_dialog(self):
        """Dialog para salvar o jogo (sobreposto)"""
        if hasattr(self, 'save_overlay') and self.save_overlay:
            return
        
        self.save_overlay = ctk.CTkFrame(
            self,
            fg_color=("#000000", "#000000"),
            width=1200,
            height=800
        )
        self.save_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        dialog_frame = ctk.CTkFrame(
            self.save_overlay,
            width=450,
            height=250,
            corner_radius=15,
            border_width=2,
            border_color=("#666666", "#444444")
        )
        dialog_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            dialog_frame,
            text=f"💾 {self.lm.t('save_game')}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            dialog_frame,
            text=self.lm.t("save_name_hint"),
            font=ctk.CTkFont(size=13)
        ).pack(pady=10)
        
        entry = ctk.CTkEntry(
            dialog_frame,
            width=350,
            height=40,
            font=ctk.CTkFont(size=14),
            placeholder_text="Ex: meu_save_01"
        )
        entry.pack(pady=15)
        entry.focus()
        
        btn_frame = ctk.CTkFrame(dialog_frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        def do_save():
            filename = entry.get().strip()
            if not re.match(r"^[A-Za-z0-9_]+$", filename):
                error_label = ctk.CTkLabel(
                    dialog_frame,
                    text=f"❌ {self.lm.t('invalid_name')}",
                    font=ctk.CTkFont(size=12),
                    text_color="#d32f2f"
                )
                error_label.pack()
                self.after(3000, error_label.destroy)
                return
            
            filename = f"{filename}.json"
            save.save_game(self.qm, filename)
            self.qm._log(self.lm.t("game_saved").format(filename=filename))
            self.close_save_dialog()
        
        ctk.CTkButton(
            btn_frame,
            text=f"💾 {self.lm.t('save')}",
            command=do_save,
            width=150,
            height=40,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text=f"❌ {self.lm.t('cancel')}",
            command=self.close_save_dialog,
            width=150,
            height=40,
            fg_color="gray40",
            hover_color="gray30"
        ).pack(side="left", padx=5)
        
        entry.bind("<Return>", lambda e: do_save())
        self.save_overlay.bind("<Escape>", lambda e: self.close_save_dialog())
        self.save_overlay.focus_set()
    
    def close_save_dialog(self):
        """Fecha o dialog de save"""
        if hasattr(self, 'save_overlay') and self.save_overlay:
            self.save_overlay.destroy()
            self.save_overlay = None
    
    # ==================== HERO DETAILS ====================
    def show_hero_details(self, hero):
        """Mostra detalhes do herói sobreposto na tela"""
        if hasattr(self, 'hero_overlay') and self.hero_overlay:
            return
        
        self.hero_overlay = ctk.CTkFrame(
            self,
            fg_color=("#000000", "#000000"),
            width=1200,
            height=800
        )
        self.hero_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        main_frame = ctk.CTkFrame(
            self.hero_overlay,
            width=600,
            height=650,
            corner_radius=15,
            border_width=2,
            border_color=("#666666", "#444444")
        )
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            width=560,
            height=580
        )
        scroll_frame.pack(padx=15, pady=15, fill="both", expand=True)
        
        # Título
        ctk.CTkLabel(
            scroll_frame,
            text=hero.name,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(5, 15))
        
        # Foto
        ctk.CTkLabel(
            scroll_frame,
            text="🧙",
            font=ctk.CTkFont(size=80)
        ).pack(pady=10)
        
        # Info básica
        info_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        info_frame.pack(pady=10, fill="x", padx=20)
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Classe
        class_frame = ctk.CTkFrame(info_frame)
        class_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(
            class_frame,
            text=f"⚔️{self.lm.t('class')}",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=2)
        ctk.CTkLabel(
            class_frame,
            text=getattr(hero, 'hero_class', 'Desconhecida'),
            font=ctk.CTkFont(size=14)
        ).pack(pady=2)
        
        # Nível
        level_frame = ctk.CTkFrame(info_frame)
        level_frame.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(
            level_frame,
            text=f"⭐ {self.lm.t('lvl_prefix')}",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=2)
        ctk.CTkLabel(
            level_frame,
            text=str(getattr(hero, 'level', 1)),
            font=ctk.CTkFont(size=14)
        ).pack(pady=2)
        
        # Stats
        if hasattr(hero, "stats") and hero.stats:
            ctk.CTkLabel(
                scroll_frame,
                text=f"📊 {self.lm.t('attribute')}",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=(15, 10))
            
            stats_frame = ctk.CTkFrame(scroll_frame)
            stats_frame.pack(pady=5, fill="x", padx=20)
            
            stats_items = list(hero.stats.items())
            for idx, (attr, value) in enumerate(stats_items):
                row = idx // 2
                col = idx % 2
                
                stat_item = ctk.CTkFrame(stats_frame)
                stat_item.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
                
                ctk.CTkLabel(
                    stat_item,
                    text=f"{attr.capitalize()}:",
                    font=ctk.CTkFont(size=12)
                ).pack(side="left", padx=(10, 5))
                
                ctk.CTkLabel(
                    stat_item,
                    text=str(value),
                    font=ctk.CTkFont(size=12, weight="bold")
                ).pack(side="right", padx=(5, 10))
            
            stats_frame.grid_columnconfigure(0, weight=1)
            stats_frame.grid_columnconfigure(1, weight=1)
        
        # História
        if hasattr(hero, "story") and hero.story:
            ctk.CTkLabel(
                scroll_frame,
                text=f"📜 {self.lm.t('story')}",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=(15, 10))
            
            story_box = ctk.CTkTextbox(
                scroll_frame,
                wrap="word",
                height=150,
                font=ctk.CTkFont(size=13)
            )
            story_box.insert("1.0", hero.story)
            story_box.configure(state="disabled")
            story_box.pack(pady=5, fill="x", padx=20)
        
        # Botão fechar
        ctk.CTkButton(
            main_frame,
            text=f"✖ {self.lm.t('close')}",
            command=self.close_hero_details,
            width=200,
            height=40,
            fg_color="gray40",
            hover_color="gray30"
        ).pack(pady=(0, 10))
        
        self.hero_overlay.bind("<Escape>", lambda e: self.close_hero_details())
        self.hero_overlay.focus_set()
    
    def close_hero_details(self):
        """Fecha os detalhes do herói"""
        if hasattr(self, 'hero_overlay') and self.hero_overlay:
            self.hero_overlay.destroy()
            self.hero_overlay = None