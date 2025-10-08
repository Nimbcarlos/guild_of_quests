# screens/gameplay/quest_details_panel.py
import customtkinter as ctk
from core.quest_success_calculator import calculate_success_chance


class QuestDetailsPanel(ctk.CTkFrame):
    """Painel central com detalhes da quest e seleção de heróis"""
    
    def __init__(self, parent, language_manager, quest_manager, on_hero_details_click):
        super().__init__(parent)
        self.lm = language_manager
        self.qm = quest_manager
        self.on_hero_details_click = on_hero_details_click
        self.pending_assignments = {}
        self.current_quest = None
        self.success_label = None
        
        self.build_ui()
    
    def build_ui(self):
        """Constrói o painel"""
        ctk.CTkLabel(
            self,
            text=f"📋 {self.lm.t('quest_details')}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(5, 5))
        
        self.content_frame = ctk.CTkScrollableFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=(0, 5))
    
    def show_quest(self, quest):
        """Mostra detalhes de uma quest"""
        self.current_quest = quest
        
        # Limpa o painel
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.pending_assignments[quest.id] = []
        self.qm.hero_manager.check_hero_unlocks(
            self.qm.completed_quests, 
            self.qm.current_turn
        )
        
        # Título da quest
        ctk.CTkLabel(
            self.content_frame,
            text=quest.name,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=10)
        
        # Tipo e dificuldade
        ctk.CTkLabel(
            self.content_frame,
            text=f"{self.lm.t('type_label')}: {quest.type} | {self.lm.t('difficulty_label')}: {quest.difficulty}"
        ).pack(pady=5)
        
        # Descrição
        desc_label = ctk.CTkLabel(
            self.content_frame,
            text=quest.description,
            wraplength=400,
            justify="left"
        )
        desc_label.pack(pady=10, padx=10)
        
        # Taxa de sucesso
        self.success_label = ctk.CTkLabel(
            self.content_frame,
            text=f"{self.lm.t('success_rate')}: --%",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.success_label.pack(pady=10)
        
        # Heróis disponíveis
        ctk.CTkLabel(
            self.content_frame,
            text=self.lm.t("available_heroes"),
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(20, 10))
        
        # Lista de heróis
        available_heroes = self.qm.hero_manager.get_available_heroes()
        
        for hero in available_heroes:
            self._create_hero_row(hero, quest)
        
        # Botão enviar para quest
        send_btn = ctk.CTkButton(
            self.content_frame,
            text=self.lm.t("send_to_quest_btn"),
            command=lambda: self._on_send_click(quest),
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        send_btn.pack(pady=20, fill="x", padx=20)
    
    def _create_hero_row(self, hero, quest):
        """Cria uma linha com info do herói"""
        hero_frame = ctk.CTkFrame(self.content_frame)
        hero_frame.pack(fill="x", padx=10, pady=5)
        
        # Grid para organizar info do herói
        hero_frame.grid_columnconfigure(0, weight=0)  # Foto
        hero_frame.grid_columnconfigure(1, weight=1)  # Nome
        hero_frame.grid_columnconfigure(2, weight=1)  # Classe
        hero_frame.grid_columnconfigure(3, weight=1)  # Level
        hero_frame.grid_columnconfigure(4, weight=0)  # Botão detalhes
        hero_frame.grid_columnconfigure(5, weight=0)  # Botão selecionar
        
        # Foto (placeholder)
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
            command=lambda: self.on_hero_details_click(hero)
        )
        details_btn.grid(row=0, column=4, padx=5)
        
        # Botão selecionar
        select_btn = ctk.CTkButton(
            hero_frame,
            text=self.lm.t('select'),
            width=100,
            command=lambda: self._toggle_hero_selection(quest, hero)
        )
        select_btn.grid(row=0, column=5, padx=5)
    
    def _toggle_hero_selection(self, quest, hero):
        """Seleciona/deseleciona herói para a quest"""
        if quest.id not in self.pending_assignments:
            self.pending_assignments[quest.id] = []
        
        if hero.id in self.pending_assignments[quest.id]:
            self.pending_assignments[quest.id].remove(hero.id)
            self.qm._log(self.lm.t("hero_removed").format(hero=hero.name, quest=quest.name))
        else:
            self.pending_assignments[quest.id].append(hero.id)
            self.qm._log(self.lm.t("hero_added").format(hero=hero.name, quest=quest.name))
        
        self._update_success_label(quest)
    
    def _update_success_label(self, quest):
        """Atualiza a taxa de sucesso"""
        hero_ids = self.pending_assignments.get(quest.id, [])
        heroes = [self.qm.get_hero(hid) for hid in hero_ids if self.qm.get_hero(hid)]
        
        if not heroes:
            self.success_label.configure(text=f"{self.lm.t('success_rate')}: --%")
            return
        
        chance = calculate_success_chance(heroes, quest)
        self.success_label.configure(text=f"{self.lm.t('success_rate')}: {chance*100:.0f}%")
    
    def _on_send_click(self, quest):
        """Handler do botão enviar"""
        hero_ids = self.pending_assignments.get(quest.id, [])
        if not hero_ids:
            self.qm._log("⚠️ Nenhum herói selecionado para esta missão.")
            return
        
        heroes = [self.qm.get_hero(hid) for hid in hero_ids if self.qm.get_hero(hid)]
        
        # Mostra diálogo inicial (será implementado no gameplay_screen)
        if hasattr(self, 'on_start_quest'):
            self.on_start_quest(quest, heroes)
    
    def clear(self):
        """Limpa o painel"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()