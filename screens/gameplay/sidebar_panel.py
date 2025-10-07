# screens/gameplay/sidebar_panel.py

from functools import partial
from customtkinter import CTkFrame, CTkButton, CTkLabel

class SidebarPanel(CTkFrame):
    def __init__(self, parent, quest_manager, language_manager, show_quest_callback):
        super().__init__(parent)
        self.qm = quest_manager
        self.lm = language_manager
        self.show_quest_callback = show_quest_callback
        self.build_sidebar()

    def build_sidebar(self):
        """Constrói e atualiza as listas de quests."""
        for widget in self.winfo_children():
            widget.destroy()

        # --- Active Quests ---
        CTkLabel(self, text=self.lm.t("active_quests"), font=("Arial", 16, "bold")).pack(pady=(10, 5))
        for quest in self.qm.get_active_quests():
            CTkButton(self, text=f"{quest.name} ({quest.type})",
                      command=lambda q=quest: self.show_quest_callback(q)).pack(pady=2, fill="x")

        # --- Available Quests ---
        CTkLabel(self, text=self.lm.t("available_quests"), font=("Arial", 16, "bold")).pack(pady=(15, 5))
        for quest in self.qm.get_available_quests():
            CTkButton(self, text=f"{quest.name} ({quest.type})",
                      command=lambda q=quest: self.show_quest_callback(q)).pack(pady=2, fill="x")

        # --- Completed Quests ---
        CTkLabel(self, text=self.lm.t("completed_quests"), font=("Arial", 16, "bold")).pack(pady=(15, 5))
        for qid in self.qm.completed_quests:
            q = self.qm.get_quest(qid)
            if q:
                CTkLabel(self, text=q.name).pack(pady=1)
