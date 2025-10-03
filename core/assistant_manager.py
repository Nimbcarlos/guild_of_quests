from core.hero import Hero

# assistant_manager.py
class AssistantManager:
    def __init__(self, language_manager, dialogue_box=None):
        self.lm = language_manager
        self.dialogue_box = dialogue_box  # instância de DialogueBox
        self.first_time = True  # 🚀 começa como primeira vez

        # Configuração fixa da assistente
        self.name = "Lyria"  
        self.portrait = "assets/img/assistant.png"

    def speak(self, key, **kwargs):
        """Mostra a fala da assistente usando o DialogueBox."""
        msg = self.lm.t(key).format(**kwargs)
        if self.dialogue_box:
            # cria um "fake hero" só para exibir
            fake_assistant = Hero(
                id="assistant",
                name=self.name,
                hero_class='Assistant',
                status="assistant_only",   # status especial para marcar
                perks=[],
                defects=[],
                story="Sua guia espiritual e companheira de aventuras.",
                photo_url=self.portrait,
                photo_body_url="assets/img/assistantfullbody.png",
                unlock_by_quest=None,
                available_from_turn=0,
                leave_on_quest=False,
                growth_curve={}
            )

            self.dialogue_box.show_dialogue([fake_assistant], "assistant_event", msg)
        else:
            print(f"[Assistente] {msg}")

    # ---------------- Eventos principais ----------------
    def on_new_quests(self, count):
        self.speak("assistant_new_quests", count=count)

    def on_heroes_return(self, hero_names):
        self.speak("assistant_heroes_return", heroes=", ".join(hero_names))

    def on_hero_level_up(self, hero_name, level):
        self.speak("assistant_level_up", hero=hero_name, level=level)

    def on_game_start(self):
        if self.first_time:
            self.speak("assistant_first_time")
            self.first_time = False
        else:
            self.speak("assistant_welcome_back")
