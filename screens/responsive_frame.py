from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock

class ResponsiveFrame(BoxLayout):
    scale_factor = NumericProperty(1)
    min_size = ListProperty([800, 600])
    max_size = ListProperty([1920, 1080])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.update_size)
        Clock.schedule_once(self._post_init, 0)  # <-- importante!

    def _post_init(self, *args):
        """Chamado depois que o layout foi adicionado à árvore."""
        self.update_size(Window, *Window.size)

    def update_size(self, window, width, height):
        """Atualiza o tamanho do frame proporcionalmente ao tamanho da janela."""
        target_w = min(max(self.min_size[0], width * self.scale_factor), self.max_size[0])
        target_h = min(max(self.min_size[1], height * self.scale_factor), self.max_size[1])

        self.size = (target_w, target_h)
        self.pos = ((width - target_w) / 2, (height - target_h) / 2)
        self.update_font_scale()

    def update_font_scale(self):
        """Escala fontes automaticamente conforme o tamanho da janela."""
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.spinner import Spinner

        for widget in self.walk():
            if isinstance(widget, (Label, Button, Spinner)):
                base_size = getattr(widget, "_base_font_size", None)
                if base_size is None:
                    widget._base_font_size = widget.font_size
                    base_size = widget.font_size
                widget.font_size = base_size * self.scale_factor
