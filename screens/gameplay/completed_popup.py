# ui/hero_popup.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from core.quest_manager import QuestManager
from core.quest_manager import LanguageManager


def show_completed_quests_popup(self, *_):
    """Abre um popup listando as quests completas e permite ver detalhes."""
    self.qm = QuestManager
    self.lm = LanguageManager

    # === Popup principal ===
    main_layout = BoxLayout(orientation="horizontal", spacing=15, padding=15)

    # === LISTA LATERAL (esquerda) ===
    quest_list_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=5)
    quest_list_box.bind(minimum_height=quest_list_box.setter('height'))
    
    quest_scroll = ScrollView(size_hint=(0.35, 1))
    quest_scroll.add_widget(quest_list_box)

    # === ÁREA DE DETALHES (direita) ===
    details_container = BoxLayout(orientation="vertical", spacing=10)
    
    # Título da quest selecionada (topo)
    quest_title_label = Label(
        text="",
        color=(0, 0, 0, 1),
        font_size=24,
        bold=True,
        markup=True,
        halign="left",
        valign="top",
        size_hint_y=None,
        height=60
    )
    quest_title_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
    
    # ScrollView para a descrição (caso seja longa)
    details_scroll = ScrollView(size_hint=(1, 1))
    
    details_label = Label(
        text=self.lm.t("select_quest_to_view"),
        color=(0, 0, 0, 1),
        font_size=16,
        halign="left",
        valign="top",
        size_hint_y=None
    )
    details_label.bind(
        texture_size=lambda instance, value: setattr(instance, 'height', value[1])
    )
    details_label.bind(
        size=lambda instance, value: setattr(instance, 'text_size', (value[0] - 20, None))
    )
    
    details_scroll.add_widget(details_label)
    
    # Adiciona título e scroll ao container
    details_container.add_widget(quest_title_label)
    details_container.add_widget(details_scroll)

    main_layout.add_widget(quest_scroll)
    main_layout.add_widget(details_container)

    # === Função interna para atualizar detalhes ===
    def show_details(quest):
        # Atualiza o título
        quest_title_label.text = f"[b]{quest.name}[/b]"
        
        # Pega os heróis que completaram essa quest
        hero_ids = qm.completed_quests.get(quest.id, set())
        
        # Monta a lista de nomes dos heróis
        hero_names = []
        if hero_ids:
            for hero_id in hero_ids:
                hero = self.qm.hero_manager.get_hero_by_id(hero_id)
                if hero:
                    hero_names.append(hero.name)
        
        # Formata o texto dos heróis
        if hero_names:
            heroes_text = f"[b]{self.lm.t('completed_by')}:[/b] {', '.join(hero_names)}\n\n"
        else:
            heroes_text = ""
        
        # Atualiza os detalhes
        details_label.text = (
            f"[b]{self.lm.t('type_label')}:[/b] {quest.type}\n"
            f"[b]{self.lm.t('difficulty_label')}:[/b] {quest.difficulty}\n\n"
            f"{heroes_text}"
            f"{quest.description}"
        )
        details_label.markup = True

    # === Preenche a lista de quests ===
    completed = qm.completed_quests
    if not completed:
        quest_list_box.add_widget(Label(
            text=self.lm.t("no_completed_quests"),
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=30
        ))
    else:
        for qid in completed:
            q = qm.get_quest(qid)
            if q:
                btn = Button(
                    text=q.name,
                    size_hint_y=None,
                    height=50,
                    background_color=(0.9, 0.85, 0.7, 1),
                    color=(0, 0, 0, 1),
                    on_release=lambda *_, quest=q: show_details(quest)
                )
                quest_list_box.add_widget(btn)

    # === Cria o popup ===
    popup = Popup(
        title=self.lm.t("completed_quests_title"),
        content=main_layout,
        size_hint=(None, None),
        size=(500, 500),
        auto_dismiss=True,
        background="assets/background.png",
        separator_color=(0, 0, 0, 0)
    )
    popup.open()
