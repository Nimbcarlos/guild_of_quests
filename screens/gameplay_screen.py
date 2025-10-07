# screens/gameplay_screen.py - CustomTkinter version
import customtkinter as ctk
from tkinter import messagebox
import re
from functools import partial
from core.quest_manager import QuestManager
from core.quest_success_calculator import calculate_success_chance
from core.dialogue_manager import DialogueManager
from core.language_manager import LanguageManager
from core.assistant_manager import AssistantManager
from screens.dialog_box import DialogueBox
import core.save_manager as save
from PIL import Image


class GameplayScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.qm = app.quest_manager
        self.lm = LanguageManager()
        self.pending_assignments = {}
        
        # Dialog e Assistant
        self.dm = DialogueManager()
        self.dialog_box = DialogueBox(self.dm, self)
        
        if self.qm.assistant:
            self.qm.assistant.dialogue_box = self.dialog_box
        
        self.qm.set_dialog_callback(self.open_dialog)
        self.qm.set_ui_callback(self.update_ui)
        self.qm.set_log_callback(self.update_log)
        
        # Build UI
        self.build_ui()
        
        # Bind ESC key
        self.bind("<Escape>", lambda e: self.open_pause_menu())
    
    def on_show(self):
        """Callback quando a tela é mostrada"""
        self.qm.hero_manager.check_hero_unlocks(
            self.qm.completed_quests, 
            self.qm.current_turn
        )
        self.qm.assistant.on_game_start()
        self.update_sidebar()
        self.update_turn_bar()
    
    def build_ui(self):
        """Constrói a interface principal"""
        # Layout principal em grid
        # Linha 0: Turn bar (span em todas as colunas)
        # Linha 1: Quest Details (esquerda) + Sidebar (direita)
        # Linha 2: Log (esquerda, abaixo da quest detail)
        
        self.grid_columnconfigure(0, weight=3, minsize=500)  # Esquerda (Quest Details + Log)
        self.grid_columnconfigure(1, weight=1, minsize=250)  # Direita (Sidebar)
        self.grid_rowconfigure(0, weight=0)  # Turn bar
        self.grid_rowconfigure(1, weight=2)  # Quest Details
        self.grid_rowconfigure(2, weight=1)  # Log
        
        # ==================== TURN BAR (topo - span 2 colunas) ====================
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
        
        # Botão de pausa (ESC)
        pause_btn = ctk.CTkButton(
            self.turn_frame,
            text="⏸ Pause (ESC)",
            command=self.open_pause_menu,
            width=120,
            fg_color="gray40"
        )
        pause_btn.pack(side="right", padx=5)
        
        # ==================== QUEST DETAILS (esquerda superior) ====================
        quest_container = ctk.CTkFrame(self)
        quest_container.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=5)
        
        ctk.CTkLabel(
            quest_container,
            text="📋 Detalhes da Quest",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(5, 5))
        
        self.quest_details_frame = ctk.CTkScrollableFrame(quest_container)
        self.quest_details_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        # ==================== SIDEBAR DIREITA ====================
        sidebar = ctk.CTkFrame(self)
        sidebar.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(2, 5), pady=5)
        
        # Active Quests
        ctk.CTkLabel(
            sidebar,
            text=self.lm.t("active_quests"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.active_quests_frame = ctk.CTkScrollableFrame(sidebar, height=200)
        self.active_quests_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Available Quests
        ctk.CTkLabel(
            sidebar,
            text=self.lm.t("available_quests"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.available_quests_frame = ctk.CTkScrollableFrame(sidebar, height=200)
        self.available_quests_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Completed Quests
        ctk.CTkLabel(
            sidebar,
            text=self.lm.t("completed_quests"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.completed_quests_frame = ctk.CTkScrollableFrame(sidebar, height=150)
        self.completed_quests_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ==================== LOG (esquerda inferior) ====================
        log_container = ctk.CTkFrame(self)
        log_container.grid(row=2, column=0, sticky="nsew", padx=(5, 2), pady=(0, 5))
        
        ctk.CTkLabel(
            log_container,
            text=self.lm.t("log_messages"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(5, 5))
        
        self.mission_log = ctk.CTkTextbox(log_container, wrap="word", state="disabled")
        self.mission_log.pack(fill="both", expand=True, padx=5, pady=(0, 5))
    
    # ==================== UPDATE METHODS ====================
    def update_turn_bar(self):
        """Atualiza o contador de turno"""
        self.turn_label.configure(
            text=f"{self.lm.t('turn_label').format(turn=self.qm.current_turn)}"
        )
    
    def update_log(self, message):
        """Adiciona mensagem ao log"""
        self.mission_log.configure(state="normal")
        self.mission_log.insert("end", f"{message}\n")
        self.mission_log.configure(state="disabled")
        self.mission_log.see("end")
    
    def update_sidebar(self):
        """Atualiza as listas de quests na sidebar"""
        # Limpa frames
        for widget in self.active_quests_frame.winfo_children():
            widget.destroy()
        for widget in self.available_quests_frame.winfo_children():
            widget.destroy()
        for widget in self.completed_quests_frame.winfo_children():
            widget.destroy()
        
        # Active Quests
        for quest in self.qm.get_active_quests():
            btn = ctk.CTkButton(
                self.active_quests_frame,
                text=f"{quest.name} ({quest.type})",
                command=partial(self.show_quest_details, quest)
            )
            btn.pack(fill="x", pady=2)
        
        # Available Quests
        for quest in self.qm.get_available_quests():
            btn = ctk.CTkButton(
                self.available_quests_frame,
                text=f"{quest.name} ({quest.type})",
                command=partial(self.show_quest_details, quest)
            )
            btn.pack(fill="x", pady=2)
        
        # Completed Quests
        for qid in self.qm.completed_quests:
            q = self.qm.get_quest(qid)
            if q:
                lbl = ctk.CTkLabel(
                    self.completed_quests_frame,
                    text=q.name,
                    anchor="w"
                )
                lbl.pack(fill="x", pady=2)
    
    def show_quest_details(self, quest):
        """Mostra detalhes da quest no painel central"""
        # Limpa o painel
        for widget in self.quest_details_frame.winfo_children():
            widget.destroy()
        
        self.pending_assignments[quest.id] = []
        self.qm.hero_manager.check_hero_unlocks(
            self.qm.completed_quests, 
            self.qm.current_turn
        )
        
        # Título da quest
        ctk.CTkLabel(
            self.quest_details_frame,
            text=quest.name,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=10)
        
        # Tipo e dificuldade
        ctk.CTkLabel(
            self.quest_details_frame,
            text=f"{self.lm.t('type_label')}: {quest.type} | {self.lm.t('difficulty_label')}: {quest.difficulty}"
        ).pack(pady=5)
        
        # Descrição
        desc_label = ctk.CTkLabel(
            self.quest_details_frame,
            text=quest.description,
            wraplength=400,
            justify="left"
        )
        desc_label.pack(pady=10, padx=10)
        
        # Taxa de sucesso
        self.success_label = ctk.CTkLabel(
            self.quest_details_frame,
            text=f"{self.lm.t('success_rate')}: --%",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.success_label.pack(pady=10)
        
        # Heróis disponíveis
        ctk.CTkLabel(
            self.quest_details_frame,
            text=self.lm.t("available_heroes"),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10))
        
        # Lista de heróis
        available_heroes = self.qm.hero_manager.get_available_heroes()
        
        for hero in available_heroes:
            hero_frame = ctk.CTkFrame(self.quest_details_frame)
            hero_frame.pack(fill="x", padx=10, pady=5)
            
            # Grid para organizar info do herói
            hero_frame.grid_columnconfigure(0, weight=0)  # Foto
            hero_frame.grid_columnconfigure(1, weight=1)  # Nome
            hero_frame.grid_columnconfigure(2, weight=1)  # Classe
            hero_frame.grid_columnconfigure(3, weight=1)  # Level
            hero_frame.grid_columnconfigure(4, weight=0)  # Botão detalhes
            hero_frame.grid_columnconfigure(5, weight=0)  # Botão selecionar
            
            # Foto (placeholder por enquanto)
            photo_label = ctk.CTkLabel(hero_frame, text="👤", font=ctk.CTkFont(size=24))
            photo_label.grid(row=0, column=0, padx=5)
            
            # Nome
            ctk.CTkLabel(hero_frame, text=hero.name).grid(row=0, column=1, padx=5, sticky="w")
            
            # Classe
            ctk.CTkLabel(
                hero_frame,
                text=f"{self.lm.t('class')}: {getattr(hero, 'hero_class', 'Unknown')}"
            ).grid(row=0, column=2, padx=5, sticky="w")
            
            # Level
            ctk.CTkLabel(
                hero_frame,
                text=f"{self.lm.t('lvl_prefix')} {getattr(hero, 'level', 1)}"
            ).grid(row=0, column=3, padx=5, sticky="w")
            
            # Botão detalhes
            details_btn = ctk.CTkButton(
                hero_frame,
                text="🔍",
                width=40,
                command=lambda h=hero: self.show_hero_details(h)
            )
            details_btn.grid(row=0, column=4, padx=5)
            
            # Botão selecionar
            select_btn = ctk.CTkButton(
                hero_frame,
                text=self.lm.t('select'),
                width=100,
                command=lambda q=quest, h=hero: self.select_hero_for_quest(q, h)
            )
            select_btn.grid(row=0, column=5, padx=5)
        
        # Botão enviar para quest
        send_btn = ctk.CTkButton(
            self.quest_details_frame,
            text=self.lm.t("send_to_quest_btn"),
            command=lambda: self.start_quest(quest),
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        send_btn.pack(pady=20, fill="x", padx=20)
    
    def select_hero_for_quest(self, quest, hero):
        """Seleciona/deseleciona herói para a quest"""
        if quest.id not in self.pending_assignments:
            self.pending_assignments[quest.id] = []
        
        if hero.id in self.pending_assignments[quest.id]:
            self.pending_assignments[quest.id].remove(hero.id)
            self.qm._log(self.lm.t("hero_removed").format(hero=hero.name, quest=quest.name))
        else:
            self.pending_assignments[quest.id].append(hero.id)
            self.qm._log(self.lm.t("hero_added").format(hero=hero.name, quest=quest.name))
        
        self.update_success_label(quest)
    
    def update_success_label(self, quest):
        """Atualiza a taxa de sucesso"""
        hero_ids = self.pending_assignments.get(quest.id, [])
        heroes = [self.qm.get_hero(hid) for hid in hero_ids if self.qm.get_hero(hid)]
        
        if not heroes:
            self.success_label.configure(text=f"{self.lm.t('success_rate')}: --%")
            return
        
        chance = calculate_success_chance(heroes, quest)
        self.success_label.configure(text=f"{self.lm.t('success_rate')}: {chance*100:.0f}%")
    
    def show_hero_details(self, hero):
        """Mostra detalhes do herói sobreposto na tela"""
        # Se já existe, não abre outro
        if hasattr(self, 'hero_overlay') and self.hero_overlay:
            return
        
        # Overlay semi-transparente de fundo
        self.hero_overlay = ctk.CTkFrame(
            self,
            fg_color=("#000000", "#000000"),
            width=1200,
            height=800
        )
        self.hero_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Frame principal centralizado
        main_frame = ctk.CTkFrame(
            self.hero_overlay,
            width=600,
            height=650,
            corner_radius=15,
            border_width=2,
            border_color=("#666666", "#444444")
        )
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Container com scroll
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            width=560,
            height=580
        )
        scroll_frame.pack(padx=15, pady=15, fill="both", expand=True)
        
        # Título com nome do herói
        ctk.CTkLabel(
            scroll_frame,
            text=hero.name,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(5, 15))
        
        # Foto/Retrato (placeholder)
        photo_label = ctk.CTkLabel(
            scroll_frame,
            text="🧙",
            font=ctk.CTkFont(size=80)
        )
        photo_label.pack(pady=10)
        
        # Info básica em um frame
        info_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        info_frame.pack(pady=10, fill="x", padx=20)
        
        # Grid para organizar info
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # Classe
        class_frame = ctk.CTkFrame(info_frame)
        class_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(
            class_frame,
            text="⚔️ Classe",
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
            text="⭐ Nível",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=2)
        ctk.CTkLabel(
            level_frame,
            text=str(getattr(hero, 'level', 1)),
            font=ctk.CTkFont(size=14)
        ).pack(pady=2)
        
        # Stats (se existir)
        if hasattr(hero, "stats") and hero.stats:
            stats_title = ctk.CTkLabel(
                scroll_frame,
                text="📊 Atributos",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            stats_title.pack(pady=(15, 10))
            
            stats_frame = ctk.CTkFrame(scroll_frame)
            stats_frame.pack(pady=5, fill="x", padx=20)
            
            # Organiza stats em grid 2 colunas
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
        
        # História (se existir)
        if hasattr(hero, "story") and hero.story:
            story_title = ctk.CTkLabel(
                scroll_frame,
                text="📜 História",
                font=ctk.CTkFont(size=16, weight="bold")
            )
            story_title.pack(pady=(15, 10))
            
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
        close_btn = ctk.CTkButton(
            main_frame,
            text="✖ Fechar",
            command=self.close_hero_details,
            width=200,
            height=40,
            fg_color="gray40",
            hover_color="gray30"
        )
        close_btn.pack(pady=(0, 10))
        
        # ESC fecha o dialog
        self.hero_overlay.bind("<Escape>", lambda e: self.close_hero_details())
        self.hero_overlay.focus_set()
    
    def close_hero_details(self):
        """Fecha os detalhes do herói"""
        if hasattr(self, 'hero_overlay') and self.hero_overlay:
            self.hero_overlay.destroy()
            self.hero_overlay = None
    
    def start_quest(self, quest):
        """Envia heróis para a quest"""
        hero_ids = self.pending_assignments.get(quest.id, [])
        if not hero_ids:
            self.qm._log("⚠️ Nenhum herói selecionado para esta missão.")
            return
        
        heroes = [self.qm.get_hero(hid) for hid in hero_ids if self.qm.get_hero(hid)]
        
        # Mostra diálogo inicial
        if heroes:
            try:
                self.dialog_box.show_dialogue(heroes, quest.id, "start")
            except Exception as e:
                print("Erro ao abrir diálogo inicial:", e)
        
        # Envia para quest
        self.qm.send_heroes_on_quest(quest.id, hero_ids)
        
        # Limpa seleção
        self.pending_assignments.pop(quest.id, None)
        
        # Limpa painel de detalhes
        for widget in self.quest_details_frame.winfo_children():
            widget.destroy()
        
        # Atualiza UI
        self.update_sidebar()
        self.update_turn_bar()
    
    # ==================== TURN & GAME FLOW ====================
    def advance_turn(self):
        """Avança o turno"""
        self.qm.advance_turn()
        self.qm._log(self.lm.t("turn_advanced").format(turn=self.qm.current_turn))
        self.update_sidebar()
        self.update_turn_bar()
    
    def update_ui(self):
        """Atualiza toda a UI"""
        self.update_sidebar()
        self.update_turn_bar()
    
    # ==================== PAUSE MENU ====================
    def open_pause_menu(self):
        """Abre menu de pausa sobreposto na tela"""
        # Se já existe, remove
        if hasattr(self, 'pause_overlay') and self.pause_overlay:
            self.close_pause_menu()
            return
        
        # Overlay semi-transparente de fundo
        self.pause_overlay = ctk.CTkFrame(
            self,
            fg_color=("#000000", "#000000"),
            width=1200,
            height=800
        )
        self.pause_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Configura opacidade (hack: usar cor com alpha)
        # Como CTk não suporta alpha direto, usamos um frame escuro
        
        # Frame do menu centralizado
        menu_frame = ctk.CTkFrame(
            self.pause_overlay,
            width=350,
            height=450,
            corner_radius=15,
            border_width=2,
            border_color=("#666666", "#444444")
        )
        menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title_label = ctk.CTkLabel(
            menu_frame,
            text=f"⏸️ {self.lm.t('pause_menu_title')}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        btn_config = {"width": 280, "height": 50, "font": ctk.CTkFont(size=14)}
        
        # Continuar (fecha o menu)
        ctk.CTkButton(
            menu_frame,
            text="▶️ Continuar",
            command=self.close_pause_menu,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            **btn_config
        ).pack(pady=8)
        
        # Salvar
        ctk.CTkButton(
            menu_frame,
            text=f"💾 {self.lm.t('save_game')}",
            command=lambda: [self.close_pause_menu(), self.save_game_dialog()],
            **btn_config
        ).pack(pady=8)
        
        # Carregar
        ctk.CTkButton(
            menu_frame,
            text=f"📂 {self.lm.t('load_game')}",
            command=lambda: [self.close_pause_menu(), self.app.show_screen("loadgame")],
            **btn_config
        ).pack(pady=8)
        
        # Menu
        ctk.CTkButton(
            menu_frame,
            text=f"🏠 {self.lm.t('back_to_menu')}",
            command=lambda: [self.close_pause_menu(), self.app.show_screen("menu")],
            fg_color="gray40",
            hover_color="gray30",
            **btn_config
        ).pack(pady=8)
        
        # Sair
        ctk.CTkButton(
            menu_frame,
            text=f"🚪 {self.lm.t('quit_game')}",
            command=self.app.quit,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            **btn_config
        ).pack(pady=8)
        
        # Bind ESC para fechar o menu
        self.pause_overlay.bind("<Escape>", lambda e: self.close_pause_menu())
        self.pause_overlay.focus_set()
    
    def close_pause_menu(self):
        """Fecha o menu de pausa"""
        if hasattr(self, 'pause_overlay') and self.pause_overlay:
            self.pause_overlay.destroy()
            self.pause_overlay = None
    
    def save_game_dialog(self):
        """Dialog para salvar o jogo (sobreposto)"""
        # Se já existe, não abre outro
        if hasattr(self, 'save_overlay') and self.save_overlay:
            return
        
        # Overlay semi-transparente de fundo
        self.save_overlay = ctk.CTkFrame(
            self,
            fg_color=("#000000", "#000000"),
            width=1200,
            height=800
        )
        self.save_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Frame do dialog centralizado
        dialog_frame = ctk.CTkFrame(
            self.save_overlay,
            width=450,
            height=250,
            corner_radius=15,
            border_width=2,
            border_color=("#666666", "#444444")
        )
        dialog_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title_label = ctk.CTkLabel(
            dialog_frame,
            text=f"💾 {self.lm.t('save_game')}",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Label de instrução
        ctk.CTkLabel(
            dialog_frame,
            text=self.lm.t("save_name_hint"),
            font=ctk.CTkFont(size=13)
        ).pack(pady=10)
        
        # Entry para o nome do save
        entry = ctk.CTkEntry(
            dialog_frame,
            width=350,
            height=40,
            font=ctk.CTkFont(size=14),
            placeholder_text="Ex: meu_save_01"
        )
        entry.pack(pady=15)
        entry.focus()
        
        # Frame dos botões
        btn_frame = ctk.CTkFrame(dialog_frame, fg_color="transparent")
        btn_frame.pack(pady=15)
        
        def do_save():
            filename = entry.get().strip()
            if not re.match(r"^[A-Za-z0-9_]+$", filename):
                # Mostra erro no próprio dialog
                error_label = ctk.CTkLabel(
                    dialog_frame,
                    text=f"❌ {self.lm.t('invalid_name')}",
                    font=ctk.CTkFont(size=12),
                    text_color="#d32f2f"
                )
                error_label.pack()
                # Remove o erro após 3 segundos
                self.after(3000, error_label.destroy)
                return
            
            filename = f"{filename}.json"
            save.save_game(self.qm, filename)
            self.qm._log(self.lm.t("game_saved").format(filename=filename))
            self.close_save_dialog()
        
        def close_dialog():
            self.close_save_dialog()
        
        # Botão Salvar
        ctk.CTkButton(
            btn_frame,
            text=f"💾 {self.lm.t('save')}",
            command=do_save,
            width=150,
            height=40,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        ).pack(side="left", padx=5)
        
        # Botão Cancelar
        ctk.CTkButton(
            btn_frame,
            text=f"❌ {self.lm.t('cancel')}",
            command=close_dialog,
            width=150,
            height=40,
            fg_color="gray40",
            hover_color="gray30"
        ).pack(side="left", padx=5)
        
        # Enter key salva
        entry.bind("<Return>", lambda e: do_save())
        
        # ESC fecha o dialog
        self.save_overlay.bind("<Escape>", lambda e: close_dialog())
        self.save_overlay.focus_set()
    
    def close_save_dialog(self):
        """Fecha o dialog de save"""
        if hasattr(self, 'save_overlay') and self.save_overlay:
            self.save_overlay.destroy()
            self.save_overlay = None
    
    def open_dialog(self, selected_heroes, quest, result):
        """Callback para abrir diálogo"""
        self.dialog_box.show_dialogue(selected_heroes, quest, result)