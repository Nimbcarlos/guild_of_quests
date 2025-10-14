from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from screens.menu_screen import MenuScreen
from screens.gameplay_screen import GameplayScreen
from screens.load_game_screen import LoadGameScreen
from screens.settings_screen import SettingsScreen  # ✅ importar a tela de settings
from screens.responsive_frame import ResponsiveFrame
from core.quest_manager import QuestManager
from core.hero_manager import HeroManager  # cria esse módulo se ainda não existir
import core.save_manager as save
import os


class GameScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.quest_manager = QuestManager()
        self.hero_manager = HeroManager()   # heróis globais

class GameApp(App):
    def build(self):
        sm = GameScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(GameplayScreen(name="gameplay"))
        sm.add_widget(LoadGameScreen(name="loadgame"))  # nova tela
        sm.add_widget(SettingsScreen(name="settings"))  # ✅ adiciona SettingsScreen
        return sm


if __name__ == "__main__":
    GameApp().run()