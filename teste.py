from kivy.config import Config

# Set the window to be non-resizable
Config.set('graphics', 'resizable', '0') 

# Set the desired fixed width and height
Config.set('graphics', 'width', '800')  # Example width
Config.set('graphics', 'height', '600') # Example height

# Import your Kivy app and run it after the configuration
from kivy.app import App
from kivy.uix.label import Label

class FixedSizeApp(App):
    def build(self):
        return Label(text='This is a fixed-size window!')

if __name__ == '__main__':
    FixedSizeApp().run()