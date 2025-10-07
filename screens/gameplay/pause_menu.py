import customtkinter as ctk

class PauseMenu(ctk.CTkToplevel):
    """
    Menu de pausa modal, implementado como CTkToplevel.
    Adiciona opções de Salvar, Carregar e Voltar ao Menu.
    """
    def __init__(self, master, quest_manager, language_manager, 
                 save_callback=None, load_callback=None, back_to_menu_callback=None):
        
        super().__init__(master)
        self.qm = quest_manager
        self.lm = language_manager
        
        # Referências aos callbacks
        self.save_callback = save_callback
        self.load_callback = load_callback
        self.back_to_menu_callback = back_to_menu_callback

        self.title("Menu de Pausa")
        self.geometry("400x450")
        
        # Configura a janela como modal
        self.transient(master)
        self.grab_set()
        
        # Adiciona um handler para o botão de fechar (X) da janela
        self.protocol("WM_DELETE_WINDOW", self.close_menu)

        self.build_ui()

    def build_ui(self):
        """Constrói os elementos de interface do menu."""
        
        # Frame central para layout (garante espaçamento uniforme)
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(main_frame, 
                     text="JOGO PAUSADO", 
                     font=("Segoe UI", 24, "bold"),
                     text_color="#FFD700"
        ).pack(pady=(10, 30))

        # --- Botões de Ação ---

        # Continuar
        ctk.CTkButton(main_frame, 
                      text=self.lm.get_string("continue_game"), # Usando get_string do LanguageManager
                      command=self.close_menu,
                      fg_color="#0078D7",
                      hover_color="#005A9E",
                      height=50
        ).pack(fill="x", pady=10)

        # Salvar
        ctk.CTkButton(main_frame, 
                      text=self.lm.get_string("save_game"),
                      command=self.save_game_and_close,
                      height=50
        ).pack(fill="x", pady=10)

        # Carregar
        ctk.CTkButton(main_frame, 
                      text=self.lm.get_string("load_game"),
                      command=self.load_game_and_close,
                      height=50
        ).pack(fill="x", pady=10)

        # Voltar ao Menu Principal
        ctk.CTkButton(main_frame, 
                      text=self.lm.get_string("back_to_menu"),
                      command=self.back_to_menu_and_close,
                      height=50
        ).pack(fill="x", pady=(20, 10))

        # Sair do Jogo (Quitar)
        # Assumindo que o master (GameplayScreen) tem acesso ao master do App (GameApp) via master.master
        ctk.CTkButton(main_frame, 
                      text=self.lm.get_string("quit_game"),
                      command=self.master.master.quit,
                      fg_color="#CC0000",
                      hover_color="#A00000",
                      height=50
        ).pack(fill="x", pady=10)
        
    # ==========================
    # Funções de Callback e Fechamento
    # ==========================
    
    def save_game_and_close(self):
        """Executa callback de salvar e fecha o menu."""
        if self.save_callback:
            self.save_callback()
        self.close_menu()
        
    def load_game_and_close(self):
        """Executa callback de carregar e fecha o menu."""
        if self.load_callback:
            self.load_callback()
        self.close_menu()

    def back_to_menu_and_close(self):
        """Executa callback de voltar ao menu e fecha o menu."""
        if self.back_to_menu_callback:
            self.back_to_menu_callback()
        self.close_menu()

    def close_menu(self):
        """Fecha o menu de pausa e libera o foco."""
        # Se a referência ao menu ainda estiver no master (GameplayScreen), a remove
        if self.master.pause_menu == self:
            self.master.pause_menu = None
            
        self.grab_release()
        self.destroy()
