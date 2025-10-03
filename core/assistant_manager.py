# assistant_manager.py
class AssistantManager:
    def __init__(self, language_manager, dialog_callback=None):
        self.lm = language_manager
        self.dialog_callback = dialog_callback  # função para exibir fala na UI

    def speak(self, key, **kwargs):
        """Mostra a fala da assistente usando as traduções do LanguageManager."""
        msg = self.lm.t(key).format(**kwargs)
        if self.dialog_callback:
            self.dialog_callback(msg)
        else:
            print(f"[Assistente] {msg}")  # fallback para debug

    # Eventos principais
    def on_new_quests(self, count):
        self.speak("assistant_new_quests", count=count)

    def on_heroes_return(self, hero_names):
        self.speak("assistant_heroes_return", heroes=", ".join(hero_names))

    def on_hero_level_up(self, hero_name, level):
        self.speak("assistant_level_up", hero=hero_name, level=level)

    def on_game_start(self):
        self.speak("assistant_game_start")
