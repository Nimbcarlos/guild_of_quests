try:
    import os
    os.environ['KIVY_NO_CONSOLELOG'] = '1'  # Remove logs verbosos (opcional)

    from kivy.config import Config
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

    from kivy.core.text import LabelBase
    # Define a fonte padrão do Kivy
    # LabelBase.register(
    #     name='Roboto',  # Substitui a fonte padrão
    #     fn_regular='assets/fonts/MaterialIcons-Regular.ttf',
    #     fn_bold='assets/fonts/MaterialIcons-Regular.ttf',
    #     fn_italic='assets/fonts/MaterialIcons-Regular.ttf',
    #     fn_bolditalic='assets/fonts/MaterialIcons-Regular.ttf'
    # )
    LabelBase.register(
        name='Icons',
        fn_regular='assets/fonts/MaterialIcons-Regular.ttf'
    )

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
    import os, sys
    from kivy.uix.screenmanager import ScreenManager, FadeTransition, SlideTransition, SwapTransition
    import traceback

    class GameScreenManager(ScreenManager):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.quest_manager = QuestManager()
            self.hero_manager = HeroManager()   # heróis globais
            self.transition = FadeTransition(duration=0.3)

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

except Exception as e:
    print(e)
    exc_type, exc_value, exc_traceback = sys.exc_info()
    
    # Pega o frame do erro (última chamada)
    tb = traceback.extract_tb(exc_traceback)
    filename, line, func, text = tb[-1]
    
    print(f"❌ Erro: {exc_type.__name__}")
    print(f"📄 Arquivo: {filename}")
    print(f"📍 Linha: {line}")
    print(f"🔧 Função: {func}")
    print(f"💬 Mensagem: {exc_value}")
    print(f"📝 Código: {text}")

'''
https://www.youtube.com/redirect?event=video_description&redir_token=QUFFLUhqbDU4V1BPTTJGNGRCZkgtMHcwOVRBQlZOTFQ3Z3xBQ3Jtc0trTjA0U0tRZ3c3dkdTWENYV0tPSnRHMGZBVnB4TTg2UzRldF9EWmtEbnBSRWMxaXFCblVJSkpQMlkyUkQ1VGptU2N1bzJoMjg1MFlPU292Vy1wNkpteGRhYnhpX05LWk5ZYlg3ampHb1FlektPMmVxWQ&q=https%3A%2F%2Ftinyurl.com%2Fmedievallofiplaylist&v=p1wg7FB1PZY
Seaside Haven Lofi
'''