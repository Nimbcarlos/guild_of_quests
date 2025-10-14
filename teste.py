# from kivy.app import App
# from kivy.uix.gridlayout import GridLayout
# from kivy.uix.label import Label
# from kivy.uix.textinput import TextInput

# class TestApp(App):
#     def build(self):
#         return self.layouted_widgets()  # replace this by `pass` for trying with KV


#     def layouted_widgets(self):
#         layout = GridLayout(rows=3, cols=2, row_force_default=True, row_default_height=40)
#         # 1st row
#         layout.add_widget(Label(text='Label 1'))
#         layout.add_widget(TextInput(text='Value 1', multiline=False, width=100))
#         # 2nd row
#         layout.add_widget(Label(text='Label 2'))
#         layout.add_widget(TextInput(text='Value 2', multiline=False, width=100))
#         # 3rd row
#         layout.add_widget(Label(text='Label 3'))
#         layout.add_widget(TextInput(text='Value 3', size_hint_x=None, width=100))
#         return layout


# if __name__ == '__main__':
#     TestApp().run()


for i in range(100):
    if i % 2 != 0:
        continue

    print(i)