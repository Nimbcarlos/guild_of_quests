# screens/gameplay/turn_bar.py
import customtkinter as ctk

class TurnBar(ctk.CTkFrame):
    def __init__(self, parent, quest_manager, language_manager, on_advance, on_pause):
        super().__init__(parent, height=50)
        self.qm = quest_manager
        self.lm = language_manager
        self.on_advance = on_advance
        self.on_pause = on_pause
        self._build_ui()

    def _build_ui(self):
        self.turn_label = ctk.CTkLabel(
            self,
            text=f"Turno: {self.qm.current_turn}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.turn_label.pack(side="left", padx=20)

        pause_btn = ctk.CTkButton(
            self,
            text="⏸ Pause (ESC)",
            command=self.on_pause,
            width=120,
            fg_color="gray40"
        )
        pause_btn.pack(side="right", padx=5)

        advance_btn = ctk.CTkButton(
            self,
            text=self.lm.t("advance_turn_btn"),
            command=self.on_advance,
            width=150
        )
        advance_btn.pack(side="right", padx=20)

    def update_turn(self):
        self.turn_label.configure(text=f"Turno: {self.qm.current_turn}")
