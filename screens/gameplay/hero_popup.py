# ui/hero_popup.py
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView


def show_hero_details(self, hero):
    """Mostra um popup com os detalhes do herói."""
    content = BoxLayout(orientation="horizontal", spacing=15, padding=15)

    # ==================== RETRATO (Esquerda) ====================
    portrait = Image(
        source=getattr(hero, "photo_body_url", "assets/ui/default_hero.png"),
        size_hint=(None, 1),
        width=180,
        allow_stretch=True,
        keep_ratio=True
    )
    content.add_widget(portrait)

    # ==================== INFORMAÇÕES (Direita) ====================
    info_container = BoxLayout(orientation="vertical", spacing=10)

    # --- Classe e Nível ---
    class_level_box = BoxLayout(orientation="vertical", spacing=3, size_hint_y=None, height=60)
    
    class_level_box.add_widget(Label(
        text=f"[b]Classe:[/b] {getattr(hero, 'hero_class', 'Desconhecida')}",
        markup=True,
        color=(0, 0, 0, 1),
        size_hint_y=None,
        height=25,
        halign="left",
        valign="middle"
    ))
    
    class_level_box.add_widget(Label(
        text=f"[b]Nível:[/b] {getattr(hero, 'level', 1)}",
        markup=True,
        color=(0, 0, 0, 1),
        size_hint_y=None,
        height=25,
        halign="left",
        valign="middle"
    ))
    
    info_container.add_widget(class_level_box)

    # --- Atributos em duas colunas ---
    if hasattr(hero, "stats") and hero.stats:
        # Container dos atributos
        stats_container = BoxLayout(orientation="vertical", spacing=5, size_hint_y=None, height=80)
        
        # Linha 1: Strength e Intelligence
        row1 = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=35)
        
        # Força (esquerda)
        strength_value = hero.stats.get("strength", 0)
        row1.add_widget(Label(
            text=f"[b]Strength:[/b] {strength_value}",
            markup=True,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.5
        ))
        
        # Inteligência (direita)
        intelligence_value = hero.stats.get("intelligence", 0)
        row1.add_widget(Label(
            text=f"[b]Intelligence:[/b] {intelligence_value}",
            markup=True,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.5
        ))
        
        stats_container.add_widget(row1)
        
        # Linha 2: Dexterity e Wisdom
        row2 = BoxLayout(orientation="horizontal", spacing=10, size_hint_y=None, height=35)
        
        # Destreza (esquerda)
        dexterity_value = hero.stats.get("dexterity", 0)
        row2.add_widget(Label(
            text=f"[b]Dexterity:[/b] {dexterity_value}",
            markup=True,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.5
        ))
        
        # Sabedoria (direita)
        wisdom_value = hero.stats.get("wisdom", 0)
        row2.add_widget(Label(
            text=f"[b]Wisdom:[/b] {wisdom_value}",
            markup=True,
            color=(0, 0, 0, 1),
            halign="left",
            valign="middle",
            size_hint_x=0.5
        ))
        
        stats_container.add_widget(row2)
        info_container.add_widget(stats_container)

    # --- História (com scroll) ---
    if hasattr(hero, "story") and hero.story:
        # Separador visual
        separator = Label(
            text="─" * 40,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=10
        )
        info_container.add_widget(separator)
        
        story_scroll = ScrollView(size_hint=(1, 1))
        
        story_label = Label(
            text=hero.story,
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

    # ==================== POPUP ====================
    popup = Popup(
        title=hero.name,
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