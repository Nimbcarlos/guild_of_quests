try:
    import os
    os.environ['KIVY_NO_CONSOLELOG'] = '1'

    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, FadeTransition
    from kivy.properties import StringProperty  # ✅ NOVO
    from screens.menu_screen import MenuScreen
    from screens.gameplay_screen import GameplayScreen
    from screens.load_game_screen import LoadGameScreen
    from screens.settings_screen import SettingsScreen
    from screens.responsive_frame import ResponsiveFrame
    from core.quest_manager import QuestManager
    from core.hero_manager import HeroManager
    from core.language_manager import LanguageManager
    from core.font_manager import FontManager
    import sys
    import traceback


    class GameScreenManager(ScreenManager):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.quest_manager = QuestManager()
            self.hero_manager = HeroManager()
            self.transition = FadeTransition(duration=0.3)


    class GameApp(App):
        # ✅ Propriedade reativa para fonte
        font_name = StringProperty("NotoSans")
        
        def build(self):
            # Registra fontes
            FontManager.register_fonts()
            
            # Cria gerenciador de idiomas
            self.lm = LanguageManager()
            
            # ✅ Define fonte inicial baseada no idioma
            self.font_name = FontManager.get_font_for_language(self.lm.language)
            
            # Cria screen manager
            sm = GameScreenManager()
            sm.add_widget(MenuScreen(name="menu"))
            sm.add_widget(GameplayScreen(name="gameplay"))
            sm.add_widget(LoadGameScreen(name="loadgame"))
            sm.add_widget(SettingsScreen(name="settings"))
            
            return sm
        
        def change_language(self, language: str):
            """
            Troca o idioma do jogo e atualiza a fonte automaticamente.
            
            Args:
                language: Código do idioma (pt, en, zh, ja, etc.)
            """
            # Atualiza idioma
            self.lm.change_language(language)
            
            # ✅ Atualiza fonte (isso dispara atualização em TODOS os widgets)
            self.font_name = FontManager.get_font_for_language(language)
            
            print(f"🌍 Idioma alterado: {language} (Fonte: {self.font_name})")


    if __name__ == "__main__":
        GameApp().run()

except Exception as e:
    print(e)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    tb = traceback.extract_tb(exc_traceback)
    filename, line, func, text = tb[-1]
    
    print(f"❌ Erro: {exc_type.__name__}")
    print(f"📄 Arquivo: {filename}")
    print(f"📍 Linha: {line}")
    print(f"🔧 Função: {func}")
    print(f"💬 Mensagem: {exc_value}")
    print(f"📝 Código: {text}")