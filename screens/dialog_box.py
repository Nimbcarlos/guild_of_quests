from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from core.hero import Hero
from typing import Optional
import random
from collections import deque
from kivy.core.window import Window

class DialogueBox:
    def __init__(self, dialogue_manager):
        """
        dialogue_manager: instância do DialogueManager
        """
        self.dm = dialogue_manager
        self.popup = None
        self.queue = deque()
        self.dialogue_label = None
        self.hero_portrait = None
        self.speaker_label = None
        self.dialogues = []
        self.current_index = 0
        self.char_index = 0
        self.full_text = ""
        self.typing_event = None
        self.heroes = []

    def get_start_dialogues(self, hero_id: str, completed_quests):
        """
        Busca falas iniciais genéricas + específicas por quest completada
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

    def show_dialogue(self, heroes, quest_id, result: str, parent_size: list):
        """
        Mostra um diálogo, enfileirando caso já exista outro ativo.
        parent_size: [width, height] do ResponsiveFrame para escalar corretamente.
        """
        self.queue.append((heroes, quest_id, result, parent_size))
        
        if not self.popup:
            self._process_next()

    def _process_next(self):
        if not self.queue:
            return
            
        heroes, quest_id, result, parent_size = self.queue.popleft()
        
        self.parent_size = parent_size

        # ✅ Agora trata tudo igual - sempre espera lista de dicts
        if isinstance(result, list):
            # Já vem formatado como [{"id": "X", "text": "..."}]
            self.dialogues = result
        elif result == "start":
            self.dialogues = self.dm.show_start_dialogues(heroes, quest_id)
        else:
            self.dialogues = self.dm.show_quest_dialogue(heroes, quest_id, result)

        if not self.dialogues:
            self.dialogues = [{"id": "narrator", "text": "..."}]

        self.heroes = heroes
        self.current_index = 0
        self.char_index = 0
        self._open_popup()

    def _open_popup(self):
        from kivy.uix.anchorlayout import AnchorLayout
        
        main_layout = BoxLayout(orientation='horizontal', spacing=15, padding=[25, 20, 25, 20])
        
        if hasattr(self, "parent_size") and self.parent_size:
            frame_width, frame_height = self.parent_size
        else:
            frame_width, frame_height = Window.width, Window.height
        
        popup_width = max(700, min(frame_width * 0.85, 1200))
        popup_height = max(180, min(frame_height * 0.22, 260))
        
        # ==================== IMAGEM ====================
        portrait_width = int(popup_height * 0.85)
        portrait_height = int(popup_height * 0.85)
        portrait_container = AnchorLayout(anchor_x='left', anchor_y='bottom', size_hint=(None, 1), width=portrait_width)
        
        self.hero_portrait = KivyImage(
            size_hint=(None, None),
            width=portrait_width,
            height=portrait_height,
            allow_stretch=True,
            keep_ratio=True
        )
        portrait_container.add_widget(self.hero_portrait)
        main_layout.add_widget(portrait_container)
        
        # ==================== TEXTO ====================
        text_layout = BoxLayout(
            orientation='vertical',
            spacing=5,
            padding=[10, 5, 10, 5],
            size_hint=(1, 1)
        )
        
        self.speaker_label = Label(
            text="",
            font_size=max(22, int(frame_height * 0.035)),
            bold=True,
            color=(0.16, 0.09, 0.06, 1),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=40
        )
        self.speaker_label.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0], None)))
        text_layout.add_widget(self.speaker_label)
        
        self.dialogue_label = Label(
            text="",
            font_size=max(16, int(frame_height * 0.024)),
            halign="left",
            valign="top",
            color=(0.16, 0.09, 0.06, 1),
            size_hint_y=1
        )
        self.dialogue_label.bind(
            size=lambda instance, value: setattr(instance, 'text_size', (value[0], None))
        )
        text_layout.add_widget(self.dialogue_label)
        
        main_layout.add_widget(text_layout)
        
        # ==================== POPUP ====================
        self.popup = Popup(
            title="",
            content=main_layout,
            size_hint=(None, None),
            size=(popup_width, popup_height),
            auto_dismiss=False,
            background="assets/background_ls.png",
            background_color=(1, 1, 1, 0.95),
            separator_height=0
        )
        
        if frame_height > 800:
            y_position = 0.12
        elif frame_height > 600:
            y_position = 0.08
        else:
            y_position = 0.05
            
        self.popup.pos_hint = {"center_x": 0.5, "y": y_position}
        self.popup.separator_color = (0, 0, 0, 0)
        
        self.popup.bind(on_touch_down=self._on_touch_next)
        self.popup.open()
        
        self._show_current_line()

    def _show_current_line(self):
        
        if self.current_index >= len(self.dialogues):
            self.popup.dismiss()
            self.popup = None
            Clock.schedule_once(lambda dt: self._process_next(), 0)
            return

        line = self.dialogues[self.current_index]

        self.full_text = ""
        resolved_hero = None

        if isinstance(line, dict):
            hero_id = str(line.get("id"))
            text = line.get("text", "")
            self.full_text = text.strip()
            
            # Busca o herói pelo ID
            resolved_hero = next((h for h in self.heroes if str(h.id) == hero_id), None)
            
        elif isinstance(line, str):
            # FALLBACK para compatibilidade
            self.full_text = line.strip()
            resolved_hero = None

        # Define o visual baseado em quem está falando
        if resolved_hero:
            self.hero_portrait.source = resolved_hero.photo_url
            self.speaker_label.text = resolved_hero.name
        else:
            self.hero_portrait.source = "assets/ui/narrator.png"
            self.speaker_label.text = "Narrador"

        # Inicia o efeito de digitação
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
