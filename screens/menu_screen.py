# screens/menu_screen.py - CustomTkinter version
import customtkinter as ctk
import core.save_manager as save


class MenuScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Configura grid para centralizar
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.build_main_menu()
    
    def build_main_menu(self):
        """Constrói a tela principal do menu com os 4 botões."""
        # Limpa widgets existentes
        for widget in self.winfo_children():
            widget.destroy()
        
        # Container centralizado
        center_frame = ctk.CTkFrame(self, fg_color="transparent")
        center_frame.grid(row=0, column=0)
        
        # Título (opcional)
        title_label = ctk.CTkLabel(
            center_frame,
            text="🎮 Quest Manager",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        title_label.pack(pady=(0, 50))
        
        # Botões
        btn_config = {
            "width": 300,
            "height": 50,
            "font": ctk.CTkFont(size=16),
            "corner_radius": 10
        }
        
        new_game_btn = ctk.CTkButton(
            center_frame,
            text="🆕 Novo Jogo",
            command=self.new_game,
            **btn_config
        )
        new_game_btn.pack(pady=10)
        
        load_game_btn = ctk.CTkButton(
            center_frame,
            text="📂 Carregar Jogo",
            command=self.show_save_files,
            **btn_config
        )
        load_game_btn.pack(pady=10)
        
        settings_btn = ctk.CTkButton(
            center_frame,
            text="⚙️ Configurações",
            command=self.open_settings,
            **btn_config
        )
        settings_btn.pack(pady=10)
        
        exit_btn = ctk.CTkButton(
            center_frame,
            text="🚪 Sair",
            command=self.exit_game,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            **btn_config
        )
        exit_btn.pack(pady=10)
    
    def new_game(self):
        """Inicia um novo jogo"""
        self.app.new_game()
    
    def show_save_files(self):
        """Mostra lista de saves disponíveis"""
        # Limpa a tela
        for widget in self.winfo_children():
            widget.destroy()
        
        # Configura grid
        self.grid_rowconfigure(0, weight=0)  # Título
        self.grid_rowconfigure(1, weight=1)  # Lista de saves
        self.grid_rowconfigure(2, weight=0)  # Botão voltar
        self.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            self,
            text="📂 Carregar Jogo",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.grid(row=0, column=0, pady=(20, 10))
        
        # Lista de saves
        save_files = save.list_saves()
        
        if not save_files:
            no_save_label = ctk.CTkLabel(
                self,
                text="Nenhum save encontrado",
                font=ctk.CTkFont(size=16)
            )
            no_save_label.grid(row=1, column=0, pady=20)
        else:
            # Frame scrollável para saves
            saves_frame = ctk.CTkScrollableFrame(
                self,
                width=500,
                height=400
            )
            saves_frame.grid(row=1, column=0, pady=10, padx=40, sticky="nsew")
            
            for filename in save_files:
                save_btn = ctk.CTkButton(
                    saves_frame,
                    text=filename,
                    command=lambda fn=filename: self._on_select_save(fn),
                    width=450,
                    height=50,
                    font=ctk.CTkFont(size=14)
                )
                save_btn.pack(pady=8)
        
        # Botão voltar
        back_btn = ctk.CTkButton(
            self,
            text="⬅️ Voltar",
            command=self.build_main_menu,
            width=200,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="gray40",
            hover_color="gray30"
        )
        back_btn.grid(row=2, column=0, pady=20)
    
    def _on_select_save(self, filename: str):
        """Handler quando o jogador escolhe um save"""
        qm = self.app.quest_manager
        
        ok = save.load_game(qm, filename=filename)
        if not ok:
            # Você pode adicionar um popup/messagebox aqui
            print(f"Erro ao carregar {filename}. Iniciando jogo novo.")
        else:
            print(f"Save carregado: {filename}")
        
        # Vai para gameplay
        self.app.show_screen("gameplay")
    
    def open_settings(self):
        """Abre a tela de configurações"""
        self.app.show_screen("settings")
    
    def exit_game(self):
        """Fecha o jogo"""
        self.app.quit()