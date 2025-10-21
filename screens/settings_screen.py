# screens/settings_screen.py
import json
import os
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.properties import BooleanProperty, NumericProperty, StringProperty, ListProperty
from core.music_manager import get_music_manager

CONFIG_FILE = "config.json"

class SettingsScreen(Screen):
    music_muted = BooleanProperty(False)
    ui_muted = BooleanProperty(False)
    music_volume = NumericProperty(100.0)  # 0-100
    ui_volume = NumericProperty(100.0)  # 0-100
    current_language = StringProperty("pt")
    screen_mode = StringProperty("Janela")
    screen_size = ListProperty([800, 600])
    available_sizes = ListProperty([
        [800, 600],
        [1024, 768],
        [1280, 720],
        [1366, 768],
        [1920, 1080]
    ])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_config()

    # ------------------- Config Load/Save -------------------
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                self.current_language = data.get("language", "pt")
                self.screen_mode = data.get("screen_mode", "Janela")
                self.screen_size = data.get("screen_size", [800, 600])
                self.music_muted = data.get("music_muted", False)
                self.ui_muted = data.get("ui_muted", False)
                self.music_volume = data.get("music_volume", 100.0)
                self.ui_volume = data.get("ui_volume", 100.0)
                
                # Aplica configurações
                Window.size = self.screen_size
                Window.fullscreen = True if self.screen_mode == "Fullscreen" else False
                
                # Aplica volume da música
                music = get_music_manager()
                music.set_volume(self.music_volume / 100.0)
                if self.music_muted:
                    music.toggle_mute()
        else:
            self.save_config()

    def save_config(self):
        data = {
            "language": self.current_language,
            "screen_mode": self.screen_mode,
            "screen_size": self.screen_size,
            "music_muted": self.music_muted,
            "ui_muted": self.ui_muted,
            "music_volume": self.music_volume,
            "ui_volume": self.ui_volume
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # ------------------- Setters -------------------
    def set_language(self, lang):
        self.current_language = lang
        print(f"Idioma definido para {lang}")
        self.save_config()

    def set_screen_mode(self, mode):
        self.screen_mode = mode
        Window.fullscreen = True if mode == "Fullscreen" else False
        print(f"Tela: {mode}")
        self.save_config()

    def set_screen_size(self, size_str):
        """size_str formato: '800x600'"""
        width, height = map(int, size_str.split('x'))
        self.screen_size = [width, height]
        Window.size = self.screen_size
        print(f"Tamanho da tela definido para {width}x{height}")
        self.save_config()

    def set_music_volume(self, value):
        """value: 0-100"""
        self.music_volume = float(value)
        music = get_music_manager()
        music.set_volume(value / 100.0)
        print(f"Volume música: {value}%")
        self.save_config()

    def set_ui_volume(self, value):
        """value: 0-100"""
        self.ui_volume = float(value)
        print(f"Volume UI: {value}%")
        self.save_config()

    def toggle_music_mute(self, checkbox, value):
        """Toggle mute da música"""
        self.music_muted = value
        music = get_music_manager()
        
        if value:
            # Mutou - para o som mas mantém o estado
            if not music.is_muted:
                music.toggle_mute()
        else:
            # Desmutou - volta o som
            if music.is_muted:
                music.toggle_mute()
        
        print(f"Música mute: {value}")
        self.save_config()

    def toggle_ui_mute(self, checkbox, value):
        """Toggle mute dos sons de UI"""
        self.ui_muted = value
        print(f"UI mute: {value}")
        self.save_config()
    
    def go_back(self):
        """Volta para o menu"""
        self.manager.current = "menu"
