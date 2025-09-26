from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from core.hero import Hero
from typing import Optional
import random


class DialogueBox:
    def __init__(self, dialogue_manager):
        """
        dialogue_manager: instância do DialogueManager
        """
        self.dm = dialogue_manager
        self.popup = None
        self.dialogue_label = None
        self.hero_portrait = None
        self.dialogues = []
        self.current_index = 0
        self.char_index = 0
        self.full_text = ""
        self.typing_event = None
        self.heroes = []

    def get_start_dialogues(self, hero_id: str, completed_quests):
        """
        Busca fal falas iniciais genéricas + específicas por quest completada
        """
        if not isinstance(completed_quests, (set, list, tuple)):
            completed_quests = set()

        hero_data = self.dm.start_dialogues.get("heroes", {}).get(str(hero_id), {})
        pool = []

        pool.extend(hero_data.get("default", []))

        for key, texts in hero_data.items():
            quest_id = key
            if quest_id in completed_quests:
                pool.extend(texts)

        if not pool:
            return None
        return random.choice(pool)

    def show_dialogue(self, heroes, quest_id, result: str):
        """
        Mostra o diálogo (inicial ou de resultado da quest).

        heroes: lista de objetos Hero
        quest_id: ID da quest (pode ser None para diálogos iniciais globais)
        result: "start" para início da quest, ou "sucesso"/"falha"/etc para resultado
        """
        self.heroes = heroes

        # Seleciona diálogos
        if result == "start":
            self.dialogues = self.dm.show_start_dialogues(heroes, quest_id)
        else:
            if quest_id is None:
                raise ValueError("quest_id deve ser fornecido para diálogos de resultado.")
            self.dialogues = self.dm.show_quest_dialogue(heroes, quest_id, result)

        # Fallback se não houver diálogos
        if not self.dialogues or not isinstance(self.dialogues, list):
            self.dialogues = ["Os heróis se preparam para a jornada..."]

        self.current_index = 0
        self.char_index = 0
        self._open_popup()

    def _open_popup(self):
        main_layout = BoxLayout(orientation='horizontal', padding=10, spacing=10)

        # Retrato
        self.hero_portrait = KivyImage(size_hint=(None, 1), width=120, allow_stretch=True, keep_ratio=True)
        main_layout.add_widget(self.hero_portrait)

        # Área de texto
        text_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, 1), padding=[10, 5, 10, 5])

        self.speaker_label = Label(
            text="",
            font_size=32,
            bold=True,
            color=(0, 0, 0, 1),
            halign="left",
            valign="top",
            size_hint=(1, None),
            text_size=(550, None)
        )
        self.speaker_label.bind(texture_size=self.speaker_label.setter("size"))
        text_layout.add_widget(self.speaker_label)

        self.dialogue_label = Label(
            text="",
            font_size=22,
            markup=True,
            halign='left',
            valign='top',
            color=(0, 0, 0, 1),
            size_hint=(1, None),
            text_size=(550, None)
        )
        self.dialogue_label.bind(texture_size=self.dialogue_label.setter('size'))
        text_layout.add_widget(self.dialogue_label)

        main_layout.add_widget(text_layout)

        self.popup = Popup(
            title="",
            content=main_layout,
            size_hint=(0.9, 0.3),
            auto_dismiss=False,
            background="assets/background_ls.png",
            background_color=(1, 1, 1, 0.8)
        )
        self.popup.pos_hint = {"center_x": 0.5, "y": 0.05}
        self.popup.separator_color = (0, 0, 0, 0)

        self.popup.bind(on_touch_down=self._on_touch_next)
        self.popup.open()

        self._show_current_line()

    def _show_current_line(self):
        if self.current_index >= len(self.dialogues):
            self.popup.dismiss()
            return

        line = self.dialogues[self.current_index]

        self.full_text = ""
        resolved_hero = None

        if isinstance(line, str):
            if self.heroes:
                hero_index = self.current_index % len(self.heroes)
                resolved_hero = self.heroes[hero_index]
                self.full_text = line.strip()
            else:
                self.full_text = line.strip()

        elif isinstance(line, dict):
            hero_id = line.get("id")
            text = line.get("text", "")
            self.full_text = text.strip()
            resolved_hero = next((h for h in self.heroes if h.id == hero_id), None)

        if resolved_hero:
            self.hero_portrait.source = resolved_hero.photo_url
            self.speaker_label.text = resolved_hero.name
        else:
            self.hero_portrait.source = "assets/ui/narrator.png"
            self.speaker_label.text = "Narrador"

        self.dialogue_label.text = ""
        self.char_index = 0
        if self.typing_event:
            self.typing_event.cancel()
        self.typing_event = Clock.schedule_interval(self._typewriter_effect, 0.05)

    def _typewriter_effect(self, dt):
        if self.char_index < len(self.full_text):
            self.dialogue_label.text += self.full_text[self.char_index]
            self.char_index += 1
        else:
            if self.typing_event:
                self.typing_event.cancel()
            self.typing_event = None
            return False

    def _on_touch_next(self, instance, touch):
        if self.typing_event:
            self.dialogue_label.text = self.full_text
            self.typing_event.cancel()
            self.typing_event = None
        else:
            self.current_index += 1
            self._show_current_line()
