from core.hero import Hero

class AssistantManager:
    def __init__(self, language_manager, dialogue_box=None):
        self.lm = language_manager
        self.dialogue_box = dialogue_box
        self.first_time = True

        # Configuração fixa da assistente
        self.id = "assistant"  # ✅ ID como string
        self.name = "Lyria"  
        self.portrait = "assets/img/assistant.png"
        
        # Cria o fake hero uma vez só
        self.fake_hero = Hero(
            id=self.id,
            name=self.name,
            hero_class='Assistant',
            status="assistant_only",
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

    def speak(self, key, **kwargs):
        """Mostra a fala da assistente usando o DialogueBox."""
        msg = self.lm.t(key).format(**kwargs)
        if self.dialogue_box:
            # Usa o DialogueBox normalmente, passando um diálogo estruturado
            dialogue = [{"id": self.id, "text": msg}]
            
            # Passa como se fosse uma quest normal
            self.dialogue_box.queue.append(
                ([self.fake_hero], "assistant_event", dialogue, None)
            )
            
            if not self.dialogue_box.popup:
                self.dialogue_box._process_next()
        else:
            print(f"[{self.name}] {msg}")

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

    def on_quests_expired(self, quest_names):
        self.speak("assistant_quest_expired", quests=", ".join(quest_names))