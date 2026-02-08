from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image as KivyImage
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
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

    def show_dialogue(self, heroes, quest_id, result, parent_size, quest_type=None, context=None):
        """
        Mostra diálogo dos heróis.
        
        Args:
            heroes: Lista de objetos Hero
            quest_id: ID da quest
            result: "start", "success" ou "failure"
            parent_size: Tamanho do widget pai (para posicionar popup)
        """
        # Determina qual método usar baseado no resultado
        if result == "start":
            # ✅ Diálogo inicial (ao começar quest)
            dialogues = self.dm.get_start_dialogue(heroes)
        else:
            # ✅ Diálogo de resultado (após completar)
            dialogues = self.dm.show_quest_dialogue(
                heroes,
                quest_id,
                result,
                quest_type,
                context=context
            )        
        # Adiciona na fila
        self.queue.append((heroes, quest_id, dialogues, parent_size))
        
        # Se não tem popup aberto, processa imediatamente
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
        popup_height = max(250, min(frame_height * 0.22, 260))
        
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
            size_hint_y=1
        )

        # ----- BOX DO SPEAKER -----
        # Aumentamos a altura para não sufocar o nome
        speaker_height = max(5, int(popup_height * 0.05)) 
        speaker_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=speaker_height
        )
        
        self.speaker_label = Label(
            text="",
            # Ajustado de 0.0035 para 0.1 (ex: 250 * 0.1 = 25px)
            font_size=max(22, int(popup_height * 0.1)), 
            bold=True,
            color=(0.16, 0.09, 0.06, 1),
            halign="left",
            valign="middle",
        )
        self.speaker_label.bind(
            size=lambda instance, value: setattr(instance, 'text_size', (value[0], None))
        )

        speaker_box.add_widget(self.speaker_label)
        text_layout.add_widget(speaker_box)

        # O ScrollView ocupará o espaço restante (0.65 do popup)
        self.scroll = ScrollView(
            size_hint=(1, None),
            height=popup_height * 0.65,
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=4,
            scroll_type=['bars', 'content']
        )

        self.dialogue_label = Label(
            text="",
            font_size=max(18, int(popup_height * 0.08)),
            halign="left",
            valign="top",
            color=(0.16, 0.09, 0.06, 1),
            markup=True,
            size_hint_y=None # Crucial para o ScrollView funcionar
        )
        
        # Ajusta a largura do texto e a altura do Label dinamicamente
        def update_label_height(instance, size):
            instance.text_size = (size[0], None) # Trava a largura
            
        def update_texture_height(instance, texture_size):
            instance.height = max(instance.parent.height if instance.parent else 0, texture_size[1])

        self.dialogue_label.bind(size=update_label_height)
        self.dialogue_label.bind(texture_size=update_texture_height)

        self.scroll.add_widget(self.dialogue_label)
        text_layout.add_widget(self.scroll)

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
            if self.popup:
                try:
                    self.popup.dismiss()
                except Exception as e:
                    print(f"[DialogueBox] Aviso: tentativa de fechar popup inexistente ({e})")
                finally:
                    self.popup = None

            # ✅ Pequeno atraso garante que evento de scroll antigo não interfira
            Clock.schedule_once(lambda dt: self._process_next(), 0.1)
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
            self.hero_portrait.source = "assets/img/assistant.png"
            self.speaker_label.text = "Lyria"

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

            self.scroll.scroll_y = 0
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
