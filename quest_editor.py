import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from core.font_manager import FontManager

QUESTS_PATH = "data/quests"
HEROES_PATH = "data/heroes"

class QuestEditor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.current_quest = None
        self.heroes_index = self.load_heroes_index()
        self.quests_index = {}
        
        # Painel esquerdo - Lista de quests
        left_panel = BoxLayout(orientation='vertical', size_hint=(0.25, 1))
        left_panel.add_widget(Label(text='Quests', size_hint_y=0.1, bold=True))
        
        self.quest_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.quest_list.bind(minimum_height=self.quest_list.setter('height'))
        
        scroll = ScrollView(size_hint=(1, 0.85))
        scroll.add_widget(self.quest_list)
        left_panel.add_widget(scroll)
        
        # Botão Nova Quest
        new_btn = Button(text='+ Nova Quest', size_hint_y=0.05)
        new_btn.bind(on_press=self.create_new_quest)
        left_panel.add_widget(new_btn)
        
        self.add_widget(left_panel)
        
        # Painel direito - Editor
        self.editor_panel = ScrollView(size_hint=(0.75, 1))
        self.editor_content = GridLayout(cols=2, spacing=2, padding=5, size_hint_y=None)
        self.editor_content.bind(minimum_height=self.editor_content.setter('height'))
        self.editor_panel.add_widget(self.editor_content)
        self.add_widget(self.editor_panel)
        
        self.load_quests()

    def load_heroes_index(self):
        heroes = {}
        if not os.path.exists(HEROES_PATH):
            return heroes
        for file in os.listdir(HEROES_PATH):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(HEROES_PATH, file), encoding="utf-8") as f:
                        data = json.load(f)
                        heroes[str(data["id"])] = data["name"]["en"]
                except Exception as e:
                    print(f"Erro ao carregar hero {file}: {e}")
        return heroes

    def load_quests(self):
        self.quest_list.clear_widgets()
        self.quests_index = {}
        
        if not os.path.exists(QUESTS_PATH):
            os.makedirs(QUESTS_PATH)
            return
            
        for file in os.listdir(QUESTS_PATH):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(QUESTS_PATH, file), encoding="utf-8") as f:
                        data = json.load(f)
                        data["_file"] = file
                        self.quests_index[str(data["id"])] = data["name"]["en"]
                        
                        btn = Button(
                            text=f"#{data['id']} - {data['name']['en'][:30]}",
                            size_hint_y=None,
                            height=40
                        )
                        btn.bind(on_press=lambda x, q=data: self.load_quest(q))
                        self.quest_list.add_widget(btn)
                except Exception as e:
                    print(f"Erro ao carregar {file}: {e}")

    def create_new_quest(self, instance):
        # Encontra próximo ID disponível
        ids = [0]
        for file in os.listdir(QUESTS_PATH):
            if file.endswith(".json"):
                try:
                    with open(os.path.join(QUESTS_PATH, file), encoding="utf-8") as f:
                        data = json.load(f)
                        ids.append(data["id"])
                except:
                    pass
        
        next_id = max(ids) + 1
        
        new_quest = {
            "id": next_id,
            "name": {"pt": "Nova Quest", "en": "New Quest", "es": "Nueva Quest", "ru": "Новый квест", "zh": "新任务", "ja": "新しいクエスト"},
            "description": {"pt": "", "en": "", "es": "", "ru": "", "zh": "", "ja": ""},
            "type": "str",
            "max_heroes": 1,
            "expired_at": 6,
            "available_from_turn": 1,
            "duration": 2,
            "difficulty": 1.0,
            "rewards": {"xp": 50},
            "required_quests": [],
            "forbidden_quests": [],
            "required_fail_quests": [],
            "required_heroes": [],
            "forbidden_heroes": [],
            "_file": f"quest_{next_id}.json"
        }
        
        self.save_quest(new_quest)
        self.load_quests()
        self.load_quest(new_quest)

    def load_quest(self, quest_data):
        self.current_quest = quest_data
        self.editor_content.clear_widgets()
        
        # Título
        self.editor_content.add_widget(Label(text='Quest Editor', size_hint_y=None, height=40, bold=True, font_size=20))
        self.editor_content.add_widget(Label(text='', size_hint_y=None, height=40))
        
        # ID
        self.add_field('ID', str(quest_data['id']), 'id', readonly=True)
        
        # Nome (multilíngue)
        self.editor_content.add_widget(Label(text='Nome:', size_hint_y=None, height=30, bold=True))
        self.editor_content.add_widget(Label(text='', size_hint_y=None, height=30))
        
        for lang in ['pt', 'en', 'es', 'ru', 'zh', 'ja']:
            self.add_field(f'  {lang.upper()}', quest_data['name'].get(lang, ''), f'name.{lang}')
        
        # Descrição (multilíngue)
        self.editor_content.add_widget(Label(text='Descrição:', size_hint_y=None, height=30, bold=True))
        self.editor_content.add_widget(Label(text='', size_hint_y=None, height=30))
        
        for lang in ['pt', 'en', 'es', 'ru', 'zh', 'ja']:
            self.add_field(f'  {lang.upper()}', quest_data['description'].get(lang, ''), f'description.{lang}', multiline=True)
        
        # Tipo (pode ser string ou lista)
        quest_type = quest_data.get('type', 'str')
        if isinstance(quest_type, list):
            type_display = ', '.join(quest_type)
        else:
            type_display = quest_type
        
        self.add_type_field('Type', quest_type, 'type')
        
        # Campos numéricos
        self.add_field('Max Heroes', str(quest_data['max_heroes']), 'max_heroes')
        self.add_field('Expired At', str(quest_data['expired_at']), 'expired_at')
        self.add_field('Available From Turn', str(quest_data['available_from_turn']), 'available_from_turn')
        self.add_field('Duration', str(quest_data['duration']), 'duration')
        self.add_field('Difficulty', str(quest_data['difficulty']), 'difficulty')
        
        # Rewards
        self.add_field('Rewards XP', str(quest_data['rewards'].get('xp', 0)), 'rewards.xp')
        
        # Listas de IDs
        self.add_list_field('Required Quests', quest_data['required_quests'], 'required_quests', 'quest')
        self.add_list_field('Forbidden Quests', quest_data['forbidden_quests'], 'forbidden_quests', 'quest')
        self.add_list_field('Required Fail Quests', quest_data['required_fail_quests'], 'required_fail_quests', 'quest')
        self.add_list_field('Required Heroes', quest_data['required_heroes'], 'required_heroes', 'hero')
        self.add_list_field('Forbidden Heroes', quest_data['forbidden_heroes'], 'forbidden_heroes', 'hero')
        
        # Botões de ação
        self.editor_content.add_widget(Label(text='', size_hint_y=None, height=20))
        self.editor_content.add_widget(Label(text='', size_hint_y=None, height=20))
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=2)
        
        save_btn = Button(text='Salvar')
        save_btn.bind(on_press=self.save_current_quest)
        btn_layout.add_widget(save_btn)
        
        delete_btn = Button(text='Deletar', background_color=(1, 0.3, 0.3, 1))
        delete_btn.bind(on_press=self.delete_current_quest)
        btn_layout.add_widget(delete_btn)
        
        self.editor_content.add_widget(btn_layout)
        self.editor_content.add_widget(Label(text='', size_hint_y=None, height=50))

    def add_field(self, label, value, field_path, readonly=False, multiline=False):
        self.editor_content.add_widget(Label(text=f'{label}:', size_hint_y=None, height=80 if multiline else 40))
        
        text_input = TextInput(
            text=value,
            multiline=multiline,
            size_hint_y=None,
            height=80 if multiline else 40,
            readonly=readonly
        )
        text_input.field_path = field_path
        self.editor_content.add_widget(text_input)

    def add_type_field(self, label, value, field_path):
        """Campo especial para type que pode ser string ou lista"""
        self.editor_content.add_widget(Label(text=f'{label}:', size_hint_y=None, height=40, bold=True))
        
        btn_layout = BoxLayout(size_hint_y=None, height=40)
        add_btn = Button(text='+ Adicionar Type', size_hint_x=0.3)
        add_btn.bind(on_press=lambda x: self.add_type_to_list(field_path))
        btn_layout.add_widget(add_btn)
        self.editor_content.add_widget(btn_layout)
        
        # Mostrar types atuais
        current_types = value if isinstance(value, list) else [value]
        
        for type_name in current_types:
            self.editor_content.add_widget(Label(text=f'  • {type_name}', size_hint_y=None, height=30))
            
            remove_btn = Button(text='X', size_hint=(0.1, None), height=30, background_color=(1, 0.3, 0.3, 1))
            remove_btn.bind(on_press=lambda x, t=type_name, fp=field_path: self.remove_type_from_list(fp, t))
            self.editor_content.add_widget(remove_btn)

    def add_type_to_list(self, field_path):
        """Adiciona um type à lista"""
        types = ['str', 'dex', 'int', 'sab', 'luta', 'athletics', 'nature', 'stealth', 
                 'thievery', 'arcana', 'investigation', 'alchemy', 'cure', 'religion', 
                 'diplomacy', 'intimidation', 'survival', 'mining', 'smithing']
        
        content = BoxLayout(orientation='vertical', padding=5, spacing=2)
        content.add_widget(Label(text='Selecione o type:'))
        
        spinner = Spinner(
            text=types[0],
            values=types,
            size_hint_y=None,
            height=40
        )
        content.add_widget(spinner)
        
        popup = Popup(title='Adicionar Type', content=content, size_hint=(0.5, 0.4))
        
        def add_action(instance):
            current_value = self.current_quest.get('type', 'str')
            
            # Converter para lista se ainda não for
            if isinstance(current_value, str):
                self.current_quest['type'] = [current_value]
            
            # Adicionar novo type se não existir
            if spinner.text not in self.current_quest['type']:
                self.current_quest['type'].append(spinner.text)
            
            self.load_quest(self.current_quest)
            popup.dismiss()
        
        add_btn = Button(text='Adicionar', size_hint_y=None, height=40)
        add_btn.bind(on_press=add_action)
        content.add_widget(add_btn)
        
        popup.open()

    def remove_type_from_list(self, field_path, type_name):
        """Remove um type da lista"""
        current_value = self.current_quest.get('type')
        
        if isinstance(current_value, list):
            if len(current_value) > 1:
                current_value.remove(type_name)
                # Se sobrar só um, pode converter de volta para string (opcional)
                # if len(current_value) == 1:
                #     self.current_quest['type'] = current_value[0]
            else:
                # Não permitir remover o último
                popup = Popup(
                    title='Erro',
                    content=Label(text='Quest precisa ter pelo menos 1 type!'),
                    size_hint=(0.5, 0.3)
                )
                popup.open()
                return
        
        self.load_quest(self.current_quest)

    def add_list_field(self, label, items, field_path, item_type):
        self.editor_content.add_widget(Label(text=f'{label}:', size_hint_y=None, height=40, bold=True))
        
        btn_layout = BoxLayout(size_hint_y=None, height=40)
        add_btn = Button(text='+', size_hint_x=0.2)
        add_btn.bind(on_press=lambda x: self.add_item_to_list(field_path, item_type))
        btn_layout.add_widget(add_btn)
        self.editor_content.add_widget(btn_layout)
        
        # Mostrar itens existentes
        for item in items:
            display_name = str(item)
            if item_type == 'quest' and str(item) in self.quests_index:
                display_name = f"#{item} - {self.quests_index[str(item)]}"
            elif item_type == 'hero' and str(item) in self.heroes_index:
                display_name = f"#{item} - {self.heroes_index[str(item)]}"
            
            self.editor_content.add_widget(Label(text=f'  • {display_name}', size_hint_y=None, height=30))
            
            remove_btn = Button(text='X', size_hint=(0.1, None), height=30, background_color=(1, 0.3, 0.3, 1))
            remove_btn.bind(on_press=lambda x, i=item, fp=field_path: self.remove_item_from_list(fp, i))
            self.editor_content.add_widget(remove_btn)

    def add_item_to_list(self, field_path, item_type):
        content = BoxLayout(orientation='vertical', padding=5, spacing=2)
        
        content.add_widget(Label(text=f'Adicionar {item_type} ID:'))
        
        text_input = TextInput(multiline=False, size_hint_y=None, height=40)
        content.add_widget(text_input)
        
        popup = Popup(title='Adicionar Item', content=content, size_hint=(0.5, 0.3))
        
        def add_action(instance):
            try:
                item_id = int(text_input.text)
                parts = field_path.split('.')
                target = self.current_quest
                for part in parts:
                    target = target[part]
                
                if item_id not in target:
                    target.append(item_id)
                    self.load_quest(self.current_quest)
                popup.dismiss()
            except ValueError:
                pass
        
        add_btn = Button(text='Adicionar', size_hint_y=None, height=40)
        add_btn.bind(on_press=add_action)
        content.add_widget(add_btn)
        
        popup.open()

    def remove_item_from_list(self, field_path, item):
        parts = field_path.split('.')
        target = self.current_quest
        for part in parts:
            target = target[part]
        
        target.remove(item)
        self.load_quest(self.current_quest)

    def save_current_quest(self, instance):
        # Coletar dados dos campos (exceto type que é gerenciado separadamente)
        for widget in self.editor_content.children:
            if isinstance(widget, TextInput) and hasattr(widget, 'field_path'):
                self.set_nested_value(self.current_quest, widget.field_path, widget.text)
        
        self.save_quest(self.current_quest)
        
        popup = Popup(
            title='Sucesso',
            content=Label(text='Quest salva com sucesso!'),
            size_hint=(0.5, 0.3)
        )
        popup.open()

    def set_nested_value(self, obj, path, value):
        parts = path.split('.')
        target = obj
        
        for part in parts[:-1]:
            target = target[part]
        
        key = parts[-1]
        
        # Tentar converter para número
        try:
            if '.' in value:
                value = float(value)
            else:
                value = int(value)
        except ValueError:
            pass
        
        target[key] = value

    def save_quest(self, quest_data):
        path = os.path.join(QUESTS_PATH, quest_data['_file'])
        data = dict(quest_data)
        data.pop('_file', None)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def delete_current_quest(self, instance):
        content = BoxLayout(orientation='vertical', padding=5, spacing=2)
        content.add_widget(Label(text='Tem certeza que deseja deletar esta quest?'))
        
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=2)
        
        def confirm_delete(x):
            path = os.path.join(QUESTS_PATH, self.current_quest['_file'])
            os.remove(path)
            popup.dismiss()
            self.load_quests()
            self.editor_content.clear_widgets()
        
        yes_btn = Button(text='Sim', background_color=(1, 0.3, 0.3, 1))
        yes_btn.bind(on_press=confirm_delete)
        btn_layout.add_widget(yes_btn)
        
        no_btn = Button(text='Não')
        no_btn.bind(on_press=lambda x: popup.dismiss())
        btn_layout.add_widget(no_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(title='Confirmar Exclusão', content=content, size_hint=(0.5, 0.3))
        popup.open()


class QuestEditorApp(App):
    def build(self):
        FontManager.register_fonts()
        return QuestEditor()


if __name__ == '__main__':
    QuestEditorApp().run()