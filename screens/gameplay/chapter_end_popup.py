from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


def show_chapter_end_popup(screen, chapter_name="Capítulo 1 Concluído"):
    qm = screen.qm
    lm = screen.lm

    # Estatísticas básicas
    current_turn = getattr(qm, "current_turn", 0)
    completed_count = len(getattr(qm, "completed_quests", []))

    hero_manager = getattr(qm, "hero_manager", None)
    heroes = getattr(hero_manager, "heroes", []) if hero_manager else []

    if isinstance(heroes, dict):
        heroes = list(heroes.values())

    hero_count = len(heroes)

    total_level = 0
    for hero in heroes:
        total_level += getattr(hero, "level", 1)

    avg_level = round(total_level / hero_count, 1) if hero_count > 0 else 0

    # Texto do resumo
    summary_text = (
        f"[b]{chapter_name}[/b]\n\n"
        f"{lm.t('chapter_1_summary')}\n"
        f"{lm.t('turns_played')}: {current_turn}\n"
        f"{lm.t('quests_completed')}: {completed_count}\n"
        f"{lm.t('average_hero_level')}: {avg_level}\n"
    )

    root = BoxLayout(
        orientation="vertical",
        spacing=12,
        padding=15
    )

    root.add_widget(Label(
        text=summary_text,
        markup=True,
        halign="center",
        valign="middle",
        color=(0, 0, 0, 1)
    ))

    btn = Button(
        text="Voltar ao Menu",
        size_hint_y=None,
        height=45
    )

    popup = Popup(
        title="Fim de Capítulo",
        content=root,
        size_hint=(None, None),
        height=400,
        width=400,
        auto_dismiss=False,
        title_color=(0, 0, 0, 1),
        title_size=1,
        separator_height=0,
        background="assets/background_ls.png",
    )

    def close_and_return(*_):
        popup.dismiss()
        screen.manager.current = "menu"

    btn.bind(on_release=close_and_return)
    root.add_widget(btn)

    popup.open()
    return popup