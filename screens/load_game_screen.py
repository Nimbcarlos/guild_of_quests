import os
import json
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
import core.save_manager as save

SAVE_DIR = "saves"

class LoadGameScreen(Screen):
    def on_enter(self):
        self.refresh_saves()

    def refresh_saves(self):
        self.ids.saves_list.clear_widgets()

        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        if not files:
            self.ids.saves_list.add_widget(Label(text="Nenhum save encontrado"))
            return

        for f in files:
            filepath = os.path.join(SAVE_DIR, f)

            # pega a data de modificação
            modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            date_str = modified.strftime("%d/%m/%Y %H:%M")

            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=40, spacing=5)

            # Label com nome + data
            row.add_widget(Label(
                text=f"{f.replace('.json', '')} - {date_str}",
                color=(0, 0, 0, 1)
            ))

            # Botão Carregar
            row.add_widget(Button(
                text="Carregar",
                size_hint_x=None,
                width=120,
                on_release=lambda _, file=f: self.load_save(file)
            ))

            # Botão Deletar
            row.add_widget(Button(
                text="Apagar",
                size_hint_x=None,
                width=100,
                on_release=lambda _, file=f: self.confirm_delete(file)
            ))

            self.ids.saves_list.add_widget(row)

    def confirm_delete(self, filename):
        """Mostra popup de confirmação antes de apagar"""
        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        content.add_widget(Label(text=f"Apagar save '{filename}'?"))

        btns = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btns.add_widget(Button(text="Cancelar", on_release=lambda *_: popup.dismiss()))
        btns.add_widget(Button(text="Apagar", on_release=lambda *_: (self.delete_save(filename), popup.dismiss())))
        content.add_widget(btns)

        popup = Popup(title="Confirmar exclusão", content=content, size_hint=(0.5, 0.3))
        popup.open()

    def delete_save(self, filename):
        filepath = os.path.join(SAVE_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        self.refresh_saves()

    def load_save(self, filename):
        """Carrega o save e entra no gameplay."""
        qm = self.manager.quest_manager
        if save.load_game(qm, filename):
            print(f"✅ Save {filename} carregado com sucesso!")
            self.manager.current = "gameplay"
        else:
            print(f"⚠️ Erro ao carregar {filename}")
