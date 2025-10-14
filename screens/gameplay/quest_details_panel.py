# screens/gameplay/quest_details_panel.py
import customtkinter as ctk
from core.quest_success_calculator import calculate_success_chance


class QuestDetailsPanel(ctk.CTkFrame):
    def show_active_quest_details(self, quest, *_):
        """
        Mostra painel com detalhes de uma QUEST ATIVA:
        - Nome, tipo, dificuldade
        - Heróis atualmente designados
        - Turnos restantes
        """
        container = self.ids.quest_details
        container.clear_widgets()

        # ========== CABEÇALHO ==========
        container.add_widget(Label(
            text=f"[b]{quest.name}[/b]",
            markup=True,
            font_size=24,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=30
        ))

        container.add_widget(Label(
            text=f"{self.lm.t('type_label')}: {quest.type} | "
                f"{self.lm.t('difficulty_label')}: {quest.difficulty}",
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=20
        ))

        container.add_widget(Label(
            text=quest.description,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=60
        ))

        # ========== TURNOS RESTANTES ==========
        remaining_turns = getattr(quest, "remaining_turns", None)
        total_turns = getattr(quest, "total_turns", None)
        if remaining_turns is not None:
            turn_text = f"{self.lm.t('remaining_turns')}: {remaining_turns}"
            if total_turns:
                turn_text += f" / {total_turns}"
        else:
            turn_text = f"{self.lm.t('remaining_turns')}: ?"

        container.add_widget(Label(
            text=turn_text,
            color=(0.2, 0.1, 0.05, 1),
            bold=True,
            size_hint_y=None,
            height=25
        ))

        # ========== HERÓIS DESIGNADOS ==========
        container.add_widget(Label(
            text=f"[b]{self.lm.t('assigned_heroes')}[/b]",
            markup=True,
            color=(0, 0, 0, 1),
            size_hint_y=None,
            height=25
        ))

        heroes_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=5)
        heroes_box.bind(minimum_height=heroes_box.setter("height"))

        assigned_heroes = getattr(quest, "assigned_heroes", [])
        if not assigned_heroes:
            heroes_box.add_widget(Label(
                text=self.lm.t("no_heroes_assigned"),
                color=(0.3, 0.3, 0.3, 1),
                italic=True,
                size_hint_y=None,
                height=30
            ))
        else:
            for hero in assigned_heroes:
                row = BoxLayout(size_hint_y=None, height=60, spacing=10)

                # Foto do herói
                if getattr(hero, "photo_url", None):
                    row.add_widget(Image(
                        source=hero.photo_url,
                        size_hint_x=None,
                        width=50
                    ))
                else:
                    row.add_widget(Label(
                        text="❓",
                        size_hint_x=None,
                        width=50
                    ))

                # Nome
                row.add_widget(Label(
                    text=hero.name,
                    color=(0, 0, 0, 1),
                    halign="left",
                    valign="middle"
                ))

                # Classe
                row.add_widget(Label(
                    text=f"{self.lm.t('class')}: {getattr(hero, 'hero_class', 'Unknown')}",
                    color=(0, 0, 0, 1),
                    halign="left",
                    valign="middle"
                ))

                # Nível
                row.add_widget(Label(
                    text=f"{self.lm.t('lvl_prefix')} {getattr(hero, 'level', 1)}",
                    color=(0, 0, 0, 1),
                    halign="left",
                    valign="middle"
                ))

                # Botão de detalhes
                row.add_widget(Button(
                    text="🔍",
                    size_hint_x=None,
                    width=50,
                    on_release=lambda *_, h=hero: self.show_hero_details(h)
                ))

                heroes_box.add_widget(row)

        # Scroll para lista de heróis
        scroll = ScrollView(size_hint_y=0.5)
        scroll.add_widget(heroes_box)
        container.add_widget(scroll)

        # ========== BOTÕES ==========
        # Se quiser dar opção de "Cancelar missão" ou "Finalizar", adiciona:
        bottom_row = BoxLayout(size_hint_y=None, height=50, spacing=10)

        cancel_btn = Button(
            text=self.lm.t("cancel_quest_btn"),
            on_release=lambda *_: self.cancel_quest(quest)
        )
        bottom_row.add_widget(cancel_btn)

        if remaining_turns == 0:
            complete_btn = Button(
                text=self.lm.t("complete_quest_btn"),
                on_release=lambda *_: self.complete_quest(quest)
            )
            bottom_row.add_widget(complete_btn)

        container.add_widget(bottom_row)
