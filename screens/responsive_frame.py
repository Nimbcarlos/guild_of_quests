from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.properties import NumericProperty, ListProperty

class ResponsiveFrame(BoxLayout):
    scale_factor = NumericProperty(0.8)
    min_size = ListProperty([800, 600])
    max_size = ListProperty([1400, 900])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_resize=self.update_size)
        self.update_size(Window, *Window.size)

    def update_size(self, window, width, height):
        # Calcula tamanho proporcional
        target_w = min(max(self.min_size[0], width * self.scale_factor), self.max_size[0])
        target_h = min(max(self.min_size[1], height * self.scale_factor), self.max_size[1])

        # Define tamanho e centraliza manualmente
        self.size = (target_w, target_h)
        self.pos = ((width - target_w) / 2, (height - target_h) / 2)
