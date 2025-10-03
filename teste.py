from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button

class ImageButtonLayout(FloatLayout):
    pass

class ImageButtonApp(App):
    def build(self):
        return ImageButtonLayout()

if __name__ == '__main__':
    ImageButtonApp().run()