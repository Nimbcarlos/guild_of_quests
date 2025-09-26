# screens/menu_screen.py
import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
import core.save_manager as save  # seu save_manager ajustado
from screens.gameplay_screen import GameplayScreen
from core.quest_manager import QuestManager
from core.hero_manager import HeroManager  # cria esse módulo se ainda não existir


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # layout principal (vertical) — guardamos em self.main_layout para reutilizar
        self.main_layout = BoxLayout(orientation="vertical", spacing=10, padding=20)
        self.add_widget(self.main_layout)
        self.build_main_menu()

    def build_main_menu(self):
        """(Re)constrói a tela principal do menu com os 4 botões."""
        self.main_layout.clear_widgets()

        new_game_btn = Button(text="Novo Jogo", size_hint_y=None, height=60)
        new_game_btn.bind(on_release=self.new_game)
        self.main_layout.add_widget(new_game_btn)

        load_game_btn = Button(text="Carregar Jogo", size_hint_y=None, height=60)
        load_game_btn.bind(on_release=self.show_save_files)
        self.main_layout.add_widget(load_game_btn)

        settings_btn = Button(text="Configurações", size_hint_y=None, height=60)
        settings_btn.bind(on_release=self.open_settings)
        self.main_layout.add_widget(settings_btn)

        exit_btn = Button(text="Sair", size_hint_y=None, height=60)
        exit_btn.bind(on_release=self.exit_game)
        self.main_layout.add_widget(exit_btn)

# Correção na Lógica do MenuScreen

    def new_game(self):
        # Exemplo (assumindo que o manager principal está no GameScreenManager):
        self.manager.quest_manager = QuestManager()  # Cria uma instância totalmente nova
        
        # E se necessário, qualquer outro manager:
        self.manager.quest_manager.hero_manager = HeroManager() # Cria um HeroManager novo, etc.

        # 2. 🔄 Remove a tela antiga de gameplay se já existir
        if self.manager.has_screen("gameplay"):
            old_screen = self.manager.get_screen("gameplay")
            self.manager.remove_widget(old_screen)

        # 3. 🆕 Recria a tela de gameplay
        # A nova tela agora usará as novas instâncias de manager zeradas.
        new_gameplay = GameplayScreen(name="gameplay")
        
        # 4. Adiciona a tela
        self.manager.add_widget(new_gameplay)

        # 5. Troca para a gameplay nova
        self.manager.current = "gameplay"

    def show_save_files(self, *args):
        print('load game')
        """Mostra lista de saves (botões)."""
        self.main_layout.clear_widgets()

        save_files = save.list_saves()  # usa a helper do save_manager
        if not save_files:
            no_save_btn = Button(text="Nenhum save encontrado — Voltar", size_hint_y=None, height=60)
            no_save_btn.bind(on_release=lambda *_: self.build_main_menu())
            self.main_layout.add_widget(no_save_btn)
            return

        for filename in save_files:
            # cada botão carrega o save e vai para gameplay
            btn = Button(text=filename, size_hint_y=None, height=50)
            # fixa filename no lambda com default arg para evitar late-binding
            btn.bind(on_release=lambda _, fn=filename: self._on_select_save(fn))
            self.main_layout.add_widget(btn)

        back_btn = Button(text="Voltar", size_hint_y=None, height=60)
        back_btn.bind(on_release=lambda *_: self.build_main_menu())
        self.main_layout.add_widget(back_btn)

    def _on_select_save(self, filename: str):
        """
        Handler quando o jogador escolhe um save.
        Carrega usando save_manager e muda para a tela de gameplay.
        """
        # garante que o QuestManager já existe no GameScreenManager
        qm = getattr(self.manager, "quest_manager", None)
        if qm is None:
            print("QuestManager não encontrado no ScreenManager. Cheque a inicialização.")
            # ainda assim tentamos mudar de tela para não travar UX:
            self.manager.current = "gameplay"
            return

        ok = save.load_game(qm, filename=filename)
        if not ok:
            # você pode abrir um Popup aqui para avisar o jogador
            print(f"Erro ao carregar {filename}. Iniciando jogo novo.")
        else:
            print(f"Save carregado: {filename}")

        # finalmente troca para gameplay (sempre)
        self.manager.current = "gameplay"

    def open_settings(self, *args):
        print("Abrir configurações (a implementar)")

    def exit_game(self, *args):
        from kivy.app import App
        App.get_running_app().stop()
