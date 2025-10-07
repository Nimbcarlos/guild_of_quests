# screens/gameplay/sidebar_panel.py
import customtkinter as ctk
from functools import partial


class SidebarPanel(ctk.CTkFrame):
    """Sidebar à direita com Active, Available e Completed quests"""
    
    def __init__(self, parent, language_manager, on_quest_click):
        super().__init__(parent)
        self.lm = language_manager
        self.on_quest_click = on_quest_click  # Callback quando clica em uma quest
        
        self.build_ui()
    
    def build_ui(self):
        """Constrói a estrutura da sidebar"""
        # Active Quests
        ctk.CTkLabel(
            self,
            text=self.lm.t("active_quests"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.active_quests_frame = ctk.CTkScrollableFrame(self, height=200)
        self.active_quests_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Available Quests
        ctk.CTkLabel(
            self,
            text=self.lm.t("available_quests"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.available_quests_frame = ctk.CTkScrollableFrame(self, height=200)
        self.available_quests_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Completed Quests
        ctk.CTkLabel(
            self,
            text=self.lm.t("completed_quests"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        self.completed_quests_frame = ctk.CTkScrollableFrame(self, height=150)
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
                command=partial(self.on_quest_click, quest)
            )
            btn.pack(fill="x", pady=2)
        
        # Available Quests
        for quest in quest_manager.get_available_quests():
            btn = ctk.CTkButton(
                self.available_quests_frame,
                text=f"{quest.name} ({quest.type})",
                command=partial(self.on_quest_click, quest)
            )
            btn.pack(fill="x", pady=2)
        
        # Completed Quests
        for qid in quest_manager.completed_quests:
            q = quest_manager.get_quest(qid)
            if q:
                lbl = ctk.CTkLabel(
                    self.completed_quests_frame,
                    text=q.name,
                    anchor="w"
                )
                lbl.pack(fill="x", pady=2)