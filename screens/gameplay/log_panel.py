# screens/gameplay/log_panel.py
import customtkinter as ctk


class LogPanel(ctk.CTkFrame):
    """Painel de log de eventos e missões"""
    
    def __init__(self, parent, language_manager):
        super().__init__(parent)
        self.lm = language_manager
        
        self.build_ui()
    
    def build_ui(self):
        """Constrói o painel de log"""
        ctk.CTkLabel(
            self,
            text=self.lm.t("log_messages"),
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(5, 5))
        
        self.log_textbox = ctk.CTkTextbox(
            self,
            wrap="word",
            state="disabled"
        )
        self.log_textbox.pack(fill="both", expand=True, padx=5, pady=(0, 5))
    
    def add_message(self, message):
        """Adiciona uma mensagem ao log"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")
    
    def clear(self):
        """Limpa o log"""
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")