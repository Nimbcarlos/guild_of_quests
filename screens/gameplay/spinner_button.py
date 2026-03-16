from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from screens.gameplay.hero_popup import show_hero_details

# ════════════════════════════════════════════════════════════════
# OPÇÃO 1: SPINNER SIMPLES (Recomendado)
# ════════════════════════════════════════════════════════════════

class InfoMenuSpinner:
    """
    Menu dropdown simples com Spinner.
    """
    
    def __init__(self, manager_instance):
        """
        Args:
            manager_instance: Instância do seu manager (para acessar self.lm, etc.)
        """
        self.manager = manager_instance
        self.lm = manager_instance.lm
    
    def create_menu_spinner(self):
        """
        Cria o Spinner com as opções.
        
        Returns:
            Spinner widget
        """
        # Define as opções do menu
        options = [
            self.lm.t("menu_select"),           # "Selecione..."
            self.lm.t("completed_quests_title"), # "Missões Completas"
            self.lm.t("hero_details_title"),     # "Detalhes dos Heróis"
            # self.lm.t("guild_stats_title"),      # "Estatísticas da Guilda" (opcional)
        ]
        
        spinner = Spinner(
            text=options[0],  # Texto inicial
            values=options[1:],  # Opções disponíveis (sem o "Selecione")
            size_hint_y=None,
            height=40,
            background_color=(0.3, 0.3, 0.3, 1),
            background_down=''
        )
        
        # Bind do evento de seleção
        spinner.bind(text=self.on_spinner_select)
        
        return spinner
    
    def on_spinner_select(self, spinner, text):
        """
        Callback quando uma opção é selecionada.
        
        Args:
            spinner: Widget Spinner
            text: Texto da opção selecionada
        """
        # Previne execução dupla
        if text == self.lm.t("menu_select"):
            return
        
        # Redireciona para a função apropriada
        if text == self.lm.t("completed_quests_title"):
            self.manager.show_completed_quests_popup()
        
        elif text == self.lm.t("hero_details_title"):
            self.show_hero_selection_popup()
        
        # elif text == self.lm.t("guild_stats_title"):
        #     self.show_guild_stats_popup()
        
        # Reseta o spinner para o estado inicial
        spinner.text = self.lm.t("menu_select")
    
    def show_hero_selection_popup(self):
        """
        Mostra popup com lista de heróis para seleção.
        """
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Título
        content.add_widget(Label(
            text=self.lm.t("select_hero"),
            size_hint_y=None,
            height=40,
            font_size=24,
            bold=True,
            color=(0, 0, 0, 1)
        ))
        
        # ScrollView para lista de heróis
        scroll = ScrollView(size_hint=(1, 1))
        hero_list = GridLayout(
            spacing=5,
            padding=5,
            cols=3
        )
        hero_list.bind(minimum_height=hero_list.setter('height'))
        
        # Adiciona botão para cada herói
        heroes = self.manager.qm.hero_manager.get_available_heroes()

        for hero in heroes:
            btn = Button(
                text=hero.name,
                size_hint_y=None,
                height=40,
            )
            btn.bind(on_release=lambda x, h=hero: show_hero_details(self, h, parent_size=self.manager.size))
            hero_list.add_widget(btn)
        
        scroll.add_widget(hero_list)
        content.add_widget(scroll)
        
        # Botão Fechar
        close_btn = Button(
            text=self.lm.t("close"),
            size_hint_y=None,
            height=50,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        
        popup = Popup(
            title=self.lm.t("hero_details_title"),
            content=content,
            size_hint=(None, None),
            width=400,
            height=450,
            background="assets/background.png",
            separator_height=0,
            title_color=(0, 0, 0, 1)
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()
    
    def show_guild_stats_popup(self):
        """
        Mostra estatísticas da guilda (exemplo adicional).
        """
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Aqui você pode adicionar suas estatísticas
        stats_text = f"""
        Guilda: {self.manager.guild_name or "Iron Rose"}
        
        Heróis Ativos: {len(self.manager.hero_manager.heroes)}
        Missões Completas: {len(self.manager.quest_manager.completed_quests)}
        Ouro Total: {self.manager.gold}
        
        Turno Atual: {self.manager.turn}
        """
        
        content.add_widget(Label(text=stats_text, font_size=16))
        
        close_btn = Button(
            text=self.lm.t("close"),
            size_hint_y=None,
            height=50
        )
        
        popup = Popup(
            title=self.lm.t("guild_stats_title"),
            content=content,
            size_hint=(0.6, 0.6)
        )
        
        close_btn.bind(on_release=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()