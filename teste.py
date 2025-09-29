from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

class MyApp(App):
    def build(self):
        # Layout principal que organiza os widgets verticalmente
        layout_principal = BoxLayout(orientation='vertical')

        # Cria o rótulo com o texto desejado
        titulo = Label(
            text='Meu Título Simples',
            size_hint_y=None, # Permite que o rótulo ocupe apenas o espaço necessário
            height=50,       # Define a altura do rótulo
            color=(0, 0.5, 1, 1) # Define a cor (azul, por exemplo)
        )

        # Adiciona o rótulo ao layout principal
        layout_principal.add_widget(titulo)

        # Adiciona um outro widget de exemplo para preencher o restante da janela
        # (pode ser outro Label, Button, etc.)
        layout_principal.add_widget(Label(
            text='Conteúdo abaixo do título',
            valign="top")
            )

        return layout_principal

if __name__ == '__main__':
    MyApp().run()