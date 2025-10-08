# screens/gameplay/sidebar_panel.py
import customtkinter as ctk
from functools import partial
from .background_helper import StretchedParchmentPanel
from .parchment_scrollable import ParchmentScrollableFrame


class SidebarPanel(StretchedParchmentPanel):
    """Sidebar à direita com Active, Available e Completed quests"""
    
    def __init__(self, parent, language_manager, on_quest_click):
        super().__init__(
            parent,
            image_path="assets/background.png"
        )
        self.lm = language_manager
        self.on_quest_click = on_quest_click
        
        self.build_ui()
    
    def build_ui(self):
        """Constrói a estrutura da sidebar"""
        # Container transparente
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # ==================== ACTIVE QUESTS ====================
        ctk.CTkLabel(
            container,
            text=self.lm.t("active_quests"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2A1810"
        ).pack(pady=(10, 5))
        
        self.active_quests_frame = ParchmentScrollableFrame(
            container,
            image_path="assets/background.png",
            height=200
        )
        self.active_quests_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ==================== AVAILABLE QUESTS ====================
        ctk.CTkLabel(
            container,
            text=self.lm.t("available_quests"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2A1810"
        ).pack(pady=(10, 5))
        
        self.available_quests_frame = ParchmentScrollableFrame(
            container,
            image_path="assets/background.png",
            height=200
        )
        self.available_quests_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # ==================== COMPLETED QUESTS ====================
        ctk.CTkLabel(
            container,
            text=self.lm.t("completed_quests"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2A1810"
        ).pack(pady=(10, 5))
        
        self.completed_quests_frame = ParchmentScrollableFrame(
            container,
            image_path="assets/parchment_bg.png",
            height=150
        )
        self.completed_quests_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    def update(self, quest_manager):
        """Atualiza as listas de quests"""
        # Limpa frames
        for widget in self.active_quests_frame.winfo_children():
            widget.destroy()
        for widget in self.available_quests_frame.winfo_children():
            widget.destroy()
        for widget in self.completed_quests_frame.winfo_children():
            widget.destroy()
        
        # Active Quests
        for quest in quest_manager.get_active_quests():
            btn = ctk.CTkButton(
                self.active_quests_frame,
                text=f"{quest.name} ({quest.type})",
                command=partial(self.on_quest_click, quest),
                fg_color="#D4C4A8",
                hover_color="#C4A577",
                text_color="#2A1810",
                border_width=1,
                border_color="#8B7355"
            )
            btn.pack(fill="x", pady=2, padx=5)
        
        # Available Quests
        for quest in quest_manager.get_available_quests():
            btn = ctk.CTkButton(
                self.available_quests_frame,
                text=f"{quest.name} ({quest.type})",
                command=partial(self.on_quest_click, quest),
                fg_color="#D4C4A8",
                hover_color="#C4A577",
                text_color="#2A1810",
                border_width=1,
                border_color="#8B7355"
            )
            btn.pack(fill="x", pady=2, padx=5)
        
        # Completed Quests (labels transparentes)
        for qid in quest_manager.completed_quests:
            q = quest_manager.get_quest(qid)
            if q:
                lbl = ctk.CTkLabel(
                    self.completed_quests_frame,
                    text=f"✓ {q.name}",
                    anchor="w",
                    text_color="#5A4830",
                    fg_color="transparent"
                )
                lbl.pack(fill="x", pady=2, padx=5)