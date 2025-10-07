# main.py - CustomTkinter version
import customtkinter as ctk
from screens.menu_screen import MenuScreen
from screens.gameplay_screen import GameplayScreen
from screens.load_game_screen import LoadGameScreen
from screens.settings_screen import SettingsScreen
from core.quest_manager import QuestManager
from core.hero_manager import HeroManager


class GameApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title("Quest Manager Game")
        self.geometry("800x600")
        
        # Tema (dark/light)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Managers globais
        self.quest_manager = QuestManager()
        self.hero_manager = HeroManager()
        
        # Container principal para as telas
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Dicionário de telas
        self.screens = {}
        
        # Inicializa as telas
        self._create_screens()
        
        # Mostra o menu inicial
        self.show_screen("menu")
    
    def _create_screens(self):
        """Cria todas as telas do jogo"""
        self.screens["menu"] = MenuScreen(self.container, self)
        self.screens["gameplay"] = GameplayScreen(self.container, self)
        self.screens["loadgame"] = LoadGameScreen(self.container, self)
        self.screens["settings"] = SettingsScreen(self.container, self)
        
        # Posiciona todas as telas no mesmo lugar
        for screen in self.screens.values():
            screen.grid(row=0, column=0, sticky="nsew")
    
    def show_screen(self, screen_name):
        """Mostra a tela especificada"""
        if screen_name in self.screens:
            self.screens[screen_name].tkraise()
            # Callback quando a tela é mostrada (útil para refresh)
            if hasattr(self.screens[screen_name], 'on_show'):
                self.screens[screen_name].on_show()
    
    def new_game(self):
        """Inicia um novo jogo"""
        # Reseta os managers
        self.quest_manager = QuestManager()
        self.hero_manager = HeroManager()
        
        # Recria a tela de gameplay
        old_gameplay = self.screens.get("gameplay")
        if old_gameplay:
            old_gameplay.destroy()
        
        self.screens["gameplay"] = GameplayScreen(self.container, self)
        self.screens["gameplay"].grid(row=0, column=0, sticky="nsew")
        
        # Vai para gameplay
        self.show_screen("gameplay")


if __name__ == "__main__":
    app = GameApp()
    app.mainloop()