"""
core/music_manager.py
Gerencia a música de fundo do jogo
"""
from kivy.core.audio import SoundLoader
import random
import os
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window


class MusicNotification(FloatLayout):
    """Notificação flutuante suave e autodestrutiva para exibir o nome da música."""

    def __init__(self, track_name: str, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = Window.size
        self.opacity = 0
        self.disabled = True  # não captura eventos

        # 🔹 Label principal (fundo translúcido e texto)
        self.label = Label(
            text=f"🎵 {track_name}",
            size_hint=(None, None),
            size=(500, 40),
            pos_hint={"center_x": 0.5, "y": 0.05},
            color=(0.9, 0.9, 0.8, 1),
            font_size=18,
            halign="center",
            valign="middle",
        )

        # fundo simples via canvas
        with self.label.canvas.before:
            from kivy.graphics import Color, RoundedRectangle
            Color(0, 0, 0, 0.6)
            self.bg = RoundedRectangle(
                size=self.label.size,
                pos=self.label.pos,
                radius=[10]
            )
        self.label.bind(size=lambda *a: setattr(self.bg, "size", self.label.size))
        self.label.bind(pos=lambda *a: setattr(self.bg, "pos", self.label.pos))

        self.add_widget(self.label)
        Window.add_widget(self)

        # 🔸 Animação: aparece suave, sobe um pouco, desaparece
        anim_in = Animation(opacity=1, duration=0.3)
        anim_slide = Animation(y=self.label.y + 30, duration=2.0)
        anim_out = Animation(opacity=0, duration=1)

        anim = anim_in + anim_slide + anim_out
        anim.bind(on_complete=lambda *a: self._cleanup())
        anim.start(self)

    def _cleanup(self):
        """Remove o widget da tela."""
        if self.parent:
            Window.remove_widget(self)

class MusicManager:
    def __init__(self, music_folder="assets/music", volume=0.5):
        """
        Inicializa o gerenciador de música.
        
        Args:
            music_folder: Pasta onde estão as músicas
            volume: Volume inicial (0.0 a 1.0)
        """
        self.music_folder = music_folder
        self.volume = volume
        self.playlists = {}  # Múltiplas playlists por contexto
        self.current_playlist = None
        self.current_track = None
        self.current_sound = None
        self.is_playing = False
        self.is_muted = False
        self.shuffle = True
        self._manual_stop = False

        # Carrega playlists por pasta
        self._load_playlists()
    
    def _load_playlists(self):
        """Carrega playlists de diferentes pastas."""
        playlist_folders = {
            'menu': 'assets/music/menu',
            'gameplay': 'assets/music/gameplay',
            'battle': 'assets/music/battle',
            'default': 'assets/music'  # fallback
        }
        
        for name, folder in playlist_folders.items():
            if os.path.exists(folder):
                self.playlists[name] = self._load_from_folder(folder)
            elif name == 'default' and os.path.exists(self.music_folder):
                self.playlists[name] = self._load_from_folder(self.music_folder)
        
    
    def _load_from_folder(self, folder):
        """Carrega músicas de uma pasta específica."""
        playlist = []
        supported_formats = ['.mp3', '.ogg', '.wav', '.flac']
        
        for filename in os.listdir(folder):
            if any(filename.lower().endswith(fmt) for fmt in supported_formats):
                filepath = os.path.join(folder, filename)
                playlist.append(filepath)
        
        if self.shuffle:
            random.shuffle(playlist)
        
        return playlist
    
    def play(self, playlist_name='default'):
        """
        Inicia/continua a reprodução de uma playlist.
        
        Args:
            playlist_name: Nome da playlist ('menu', 'gameplay', 'battle', 'default')
        """
        # IMPORTANTE: Se já está tocando, não faz nada
        if self.is_playing and self.current_sound and self.current_sound.state == 'play':
            return
        
        # Se está pedindo para tocar a mesma playlist que já estava tocando
        if self.current_playlist == playlist_name and self.current_sound:
            self.is_playing = True
            return
        
        # Se mudou de playlist, para a atual e começa nova
        if self.current_playlist != playlist_name:
            if self.current_sound:
                self.current_sound.stop()
            self.current_track = None
            self.current_playlist = playlist_name
        
        playlist = self.playlists.get(playlist_name, self.playlists.get('default', []))
        
        if not playlist:
            return
        
        if self.is_muted:
            return
        
        # Se não tem música tocando, inicia uma nova
        if self.current_track is None or not self.current_sound:
            self._play_next(playlist)
        
        self.is_playing = True
    
    def _play_next(self, playlist=None):
        if playlist is None:
            playlist = self.playlists.get(self.current_playlist, [])
        if not playlist:
            return

        if self.current_sound:
            self.current_sound.stop()

        if self.current_track is None:
            self.current_track = 0
        else:
            self.current_track = (self.current_track + 1) % len(playlist)

        music_path = playlist[self.current_track]
        self.current_sound = SoundLoader.load(music_path)

        if self.current_sound:
            self.current_sound.volume = self.volume if not self.is_muted else 0
            self.current_sound.loop = False
            self.current_sound.bind(on_stop=self._on_track_end)
            self.current_sound.play()

            track_name = os.path.basename(music_path).replace("_", " ")

            # 🔔 Mostra popup flutuante com o nome da música
            Clock.schedule_once(lambda dt: MusicNotification(track_name), 0)

    def _on_track_end(self, *args):
        """Callback quando a música termina - toca a próxima."""
        if self._manual_stop:
            # Reset flag e não toca mais nada
            self._manual_stop = False
            return

        if self.is_playing:
            playlist = self.playlists.get(self.current_playlist, [])
            self._play_next(playlist)
    
    def stop(self):
        """Para a música completamente."""
        if self.current_sound:
            self._manual_stop = True  # marca que foi parada manualmente
            self.current_sound.unbind(on_stop=self._on_track_end)  # evita loop
            self.current_sound.stop()
            self.current_sound = None
        self.is_playing = False
    
    def set_volume(self, volume):
        """
        Define o volume da música.
        
        Args:
            volume: float entre 0.0 (mudo) e 1.0 (máximo)
        """
        self.volume = max(0.0, min(1.0, volume))
        if self.current_sound and not self.is_muted:
            self.current_sound.volume = self.volume
    
    def toggle_mute(self):
        """Liga/desliga o mute."""
        self.is_muted = not self.is_muted
        if self.current_sound:
            self.current_sound.volume = 0 if self.is_muted else self.volume
    
    def next_track(self):
        """Pula para a próxima música."""
        if self.is_playing:
            self._play_next()
    
    def previous_track(self):
        """Volta para a música anterior."""
        if self.playlist and self.is_playing:
            self.current_track = (self.current_track - 2) % len(self.playlist)
            self._play_next()
    
    def set_shuffle(self, shuffle):
        """Liga/desliga o shuffle."""
        self.shuffle = shuffle
        if shuffle:
            random.shuffle(self.playlist)

    def pause(self):
        """Pausa a música atual sem resetar."""
        if self.current_sound and self.is_playing:
            self.current_sound.stop()
            self.is_playing = False

# Instância global (singleton)
_music_manager = None

def get_music_manager():
    """Retorna a instância global do MusicManager."""
    global _music_manager
    if _music_manager is None:
        _music_manager = MusicManager()
    return _music_manager