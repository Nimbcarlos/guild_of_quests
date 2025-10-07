import customtkinter as ctk
from datetime import datetime


class LogPanel(ctk.CTkFrame):
    """
    Painel lateral ou inferior que exibe o histórico de eventos do jogo:
    - Início e fim de missões
    - Resultados
    - Ações dos heróis
    - Mensagens narrativas
    """

    def __init__(self, master, quest_manager, language_manager): # Adicionando os managers
        super().__init__(master, fg_color="#1e1e1e", corner_radius=10)
        self.configure(border_width=1, border_color="#3a3a3a")
        self.qm = quest_manager
        self.lm = language_manager

        # 🏷️ Cabeçalho
        self.title_label = ctk.CTkLabel(
            self,
            text="Registro de Eventos",
            font=("Segoe UI", 18, "bold"),
            text_color="#FFD700",
        )
        self.title_label.pack(pady=(8, 5))

        # 📜 Caixa de texto de log
        self.textbox = ctk.CTkTextbox(
            self,
            width=500,
            height=200,
            font=("Consolas", 13),
            wrap="word",
            fg_color="#121212",
            text_color="#E0E0E0",
        )
        self.textbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.textbox.insert("end", "[Sistema] Log inicializado.\n")
        self.textbox.configure(state="disabled")

    # =====================================================
    # Funções de uso público
    # =====================================================

    def add_log(self, message, sender="Sistema"): # Método renomeado de 'add_log' para 'add_message' no gameplay_screen, mas mantendo 'add_log' aqui.
        """
        Adiciona uma nova linha ao log, com timestamp e remetente.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {sender}: {message}\n"

        self.textbox.configure(state="normal")
        self.textbox.insert("end", formatted)
        self.textbox.configure(state="disabled")
        self.textbox.see("end")

    def refresh(self):
        """Método placeholder para ser chamado por update_ui (pode ser usado para limpar logs antigos, etc)."""
        pass # Atualmente não faz nada, mas é necessário para o callback update_ui

    def clear_log(self):
        """Limpa completamente o painel de log."""
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", "[Sistema] Log limpo.\n")
        self.textbox.configure(state="disabled")
