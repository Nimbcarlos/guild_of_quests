import customtkinter as ctk

class DialoguePanel(ctk.CTkFrame):
    """
    Painel de diálogos do jogo, implementado como um overlay (modal).
    Gerenciado via place() no GameplayScreen.
    """

    def __init__(self, master, dialogue_manager):
        # Aumentei o nível de opacidade do fundo para simular um popup
        super().__init__(master, fg_color="#181818", corner_radius=15, border_width=2, border_color="#FFD700")
        self.dm = dialogue_manager
        
        # O frame principal que contém o conteúdo (Label e Botão)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 💬 Rótulo do Texto Principal
        self.dialogue_label = ctk.CTkLabel(
            self.content_frame,
            text="",
            font=("Segoe UI", 16),
            justify="left",
            wraplength=450,
            anchor="w",
            text_color="#F0F0F0"
        )
        self.dialogue_label.pack(fill="both", expand=True, pady=(0, 15))

        # ❌ Botão de Fechar
        self.btn_close = ctk.CTkButton(
            self.content_frame,
            text="Fechar Diálogo",
            command=self.hide_dialogue,
            fg_color="#005A9E",
            hover_color="#0078D7",
            font=("Segoe UI", 14, "bold"),
            width=200
        )
        self.btn_close.pack(pady=5)
        
        self.current_callback = None

        # Configuração inicial: o painel é pequeno, mas se expandirá ao ser colocado.
        self.configure(width=500, height=300)


    def show_dialogue(self, heroes, quest, result, callback=None):
        """
        Mostra um diálogo baseado nos heróis e no resultado da quest.
        """
        self.current_callback = callback
        
        # 1. Gerar o texto narrativo
        # Para fins de demonstração, vamos gerar um texto simples aqui:
        text = f"Resultado da Missão: {'SUCESSO' if result.get('success') else 'FALHA'}\n\n"
        
        # Supondo que o quest_manager já tenha colocado o texto narrativo na quest ou resultado
        narrative = self.dm.generate_dialogue(heroes, quest, result)
        text += narrative
        
        # 2. Atualizar o Label e mostrar o painel
        self.dialogue_label.configure(text=text)
        
        # Coloca o painel na tela (overlay)
        # Assumindo que o master (GameplayScreen) lida com o place(relx=0.5, rely=0.85, anchor="center")
        self.master.dialogue_panel.place(relx=0.5, rely=0.5, anchor="center")
        self.master.dialogue_panel.lift() # Garante que está no topo

    def show_assistant_message(self, message):
        """
        Exibe a fala da assistente.
        """
        # Define o conteúdo da mensagem da assistente e mostra
        text = f"Algaza-Ha diz: \"{message}\""
        self.dialogue_label.configure(text=text)
        self.btn_close.configure(text="Ok, entendi.")
        
        self.master.dialogue_panel.place(relx=0.5, rely=0.5, anchor="center")
        self.master.dialogue_panel.lift()

    def hide_dialogue(self, *args):
        """
        Oculta o painel e executa o callback, se houver.
        """
        # Oculta o painel
        self.master.dialogue_panel.place_forget()
        
        # Reseta o botão para o texto padrão
        self.btn_close.configure(text="Fechar Diálogo")

        if self.current_callback:
            self.current_callback()
            self.current_callback = None
