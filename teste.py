from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.app import App

# Register the font (optional, for global use)
LabelBase.register(name='Icons', fn_regular='assets/fonts/MaterialIcons-Regular.ttf')

class IconApp(App):
    def build(self):
        # Using the registered font
        icon_label = Label(text=u'\uf013', markup=True, font_size='64sp')
        # Directly specifying font_name
        another_icon = Label(text=u'\uf005', font_name='assets/fonts/MaterialIcons-Regular.ttf', font_size='64sp')
        return icon_label # or another_icon, or a layout containing both
    
if __name__ == "__main__":
    IconApp().run()
