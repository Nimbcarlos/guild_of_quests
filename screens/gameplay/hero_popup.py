# ui/hero_popup.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
import json
import os
from core.language_manager import LanguageManager


def load_hero_data(hero_id, language="en"):
    """
    Carrega os dados traduzidos do herói do arquivo data/{language}/heroes.json
    """
    try:
        filepath = f"data/heroes.json"

        if not os.path.exists(filepath):
            print(f"[HeroPopup] Arquivo não encontrado: {filepath}")
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            heroes_list = json.load(f)

        for hero_data in heroes_list:
            if hero_data.get("id") == hero_id:
                return hero_data

        print(f"[HeroPopup] Herói ID {hero_id} não encontrado em {filepath}")
        return None

    except Exception as e:
        print(f"[HeroPopup] Erro ao carregar dados do herói: {e}")
        import traceback
        traceback.print_exc()
        return None


def show_hero_details(screen_instance, hero):
    """
    Mostra um popup com os detalhes do herói traduzido.
    """
    # Usa o LanguageManager da tela (já instanciado)
    lm = getattr(screen_instance, "lm", LanguageManager())
    current_lang = lm.language

    # Carrega dados traduzidos
    hero_data = load_hero_data(hero.id, current_lang)

    if not hero_data:
        hero_data = {
            "name": hero.name,
            "hero_class": getattr(hero, "hero_class", "Unknown"),
            "story": getattr(hero, "story", "")
        }

    content = BoxLayout(orientation="horizontal", spacing=5, padding=5)

    # ========== Retrato (esquerda) ==========
    portrait = Image(
        source=getattr(hero, "photo_body_url", "assets/img/default_hero.png"),
        size_hint=(None, 1),
        width=180,
        allow_stretch=True,
        keep_ratio=True
    )
    content.add_widget(portrait)

    # ========== Informações (direita) ==========
    info_container = BoxLayout(orientation="vertical", spacing=5)

    # Classe e nível
    class_level_box = BoxLayout(orientation="vertical", spacing=3, size_hint_y=None, height=60)

    class_field = hero_data.get('hero_class', 'Unknown')
    if isinstance(class_field, dict):
        class_text = str(class_field.get(current_lang, class_field.get("en", "")))
    else:
        class_text = class_field

    class_level_box.add_widget(Label(
        text=class_text,
        markup=True,
        color=(0, 0, 0, 1),
        size_hint_y=None,
        height=25,
        halign="left",
        valign="middle"
    ))

    class_level_box.add_widget(Label(
        text=f"[b]{lm.t('level_label')}:[/b] {getattr(hero, 'level', 1)}",
        markup=True,
        color=(0, 0, 0, 1),
        size_hint_y=None,
        height=25,
        halign="left",
        valign="middle"
    ))

    info_container.add_widget(class_level_box)

    # ========== Atributos ==========
    hero_stats = None

    # 1️⃣ Se o herói já tem stats calculados
    if hasattr(hero, "stats") and hero.stats:
        hero_stats = hero.stats

    # 2️⃣ Caso contrário, tenta usar o growth_curve
    else:
        growth = getattr(hero, "growth_curve", None)
        current_level = str(getattr(hero, "level", 1))
        hero_stats = {}

        if growth:
            if isinstance(growth, str):
                try:
                    growth = json.loads(growth)
                except Exception as e:
                    print(f"[HeroPopup] Erro ao decodificar growth_curve: {e}")
                    growth = {}

            if isinstance(growth, dict):
                hero_stats = growth.get(current_level, {})

    if hero_stats:
        stats_container = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None, height=80)

        # Linha 1
        row1 = BoxLayout(orientation="horizontal", spacing=5, size_hint_y=None, height=35)
        row1.add_widget(Label(
            text=f"[b]{lm.t('strength')}:[/b] {hero_stats.get('strength', 0)}",
            markup=True,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.5
        ))
        row1.add_widget(Label(
            text=f"[b]{lm.t('intelligence')}:[/b] {hero_stats.get('intelligence', 0)}",
            markup=True,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.5
        ))
        stats_container.add_widget(row1)

        # Linha 2
        row2 = BoxLayout(orientation="horizontal", spacing=5, size_hint_y=None, height=35)
        row2.add_widget(Label(
            text=f"[b]{lm.t('dexterity')}:[/b] {hero_stats.get('dexterity', 0)}",
            markup=True,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.5
        ))
        row2.add_widget(Label(
            text=f"[b]{lm.t('wisdom')}:[/b] {hero_stats.get('wisdom', 0)}",
            markup=True,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.5
        ))
        stats_container.add_widget(row2)

        info_container.add_widget(stats_container)

    # ========== História ==========
    story_field = hero_data.get("story", "")
    if isinstance(story_field, dict):
        story_text = str(story_field.get(current_lang, story_field.get("en", "")))
    else:
        story_text = story_field

    class_en = class_field.get("en", "")

    if story_text:
        separator = Image(
            source=f"assets/img/{class_en}.png",
            size_hint=(None, None),  # Permite definir largura e altura fixas
            width=300,
            height=50,               # Altura livre (não proporcional)
            allow_stretch=True,      # Permite distorcer
            keep_ratio=False,        # Ignora proporção original
        )
        # separator = Label(
        #     text="=" * 30,
        #     color=(0.5, 0.5, 0.5, 1),
        #     size_hint_y=None,
        #     height=10
        # )
        info_container.add_widget(separator)

        story_scroll = ScrollView(size_hint=(1, 1))
        story_label = Label(
            text=story_text,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            halign="left",
            valign="top",
            markup=True
        )
        story_label.bind(
            texture_size=lambda inst, val: setattr(story_label, "height", val[1])
        )
        story_label.bind(
            size=lambda inst, val: setattr(story_label, "text_size", (val[0] - 20, None))
        )

        story_scroll.add_widget(story_label)
        info_container.add_widget(story_scroll)

    content.add_widget(info_container)

    # ========== Popup ==========
    name_field = hero_data.get("name", "Hero")
    if isinstance(name_field, dict):
        name_text = str(name_field.get(current_lang, name_field.get("en", "")))
    else:
        name_text = name_field

    popup = Popup(
        title=name_text,
        content=content,
        title_align='center',
        title_size=28,
        title_color=(0, 0, 0, 1),
        separator_color=(0.3, 0.2, 0.1, 1),
        separator_height=2,
        background="assets/background.png",
        size_hint=(None, None),
        size=(550, 500),
        auto_dismiss=True
    )
    popup.open()
