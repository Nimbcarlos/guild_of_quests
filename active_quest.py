from core.hero import Hero
from core.quest import Quest

class ActiveQuest:
    def __init__(self, heroes: list[Hero], quest_data: Quest, end_time: float):
        self.heroes = heroes                # lista de heróis na missão
        self.quest_data = quest_data        # dados da quest
        self.start_time = end_time - quest_data.duration
        self.end_time = end_time            # quando termina
        self.is_completed = False           # status da missão
        self.is_failed = False              # caso queira expandir depois

    def to_dict(self):
        return {
            "heroes": [hero.name for hero in self.heroes],
            "quest": self.quest_data.to_dict(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "is_completed": self.is_completed,
            "is_failed": self.is_failed
        }
