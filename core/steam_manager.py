# core/steam_manager.py
"""
Gerenciador de integração com Steam usando SteamworksPy
"""

try:
    from steamworks import STEAMWORKS
    STEAM_AVAILABLE = True
except ImportError:
    print("[SteamManager] SteamworksPy não disponível - rodando offline")
    STEAM_AVAILABLE = False


class SteamManager:
    def __init__(self):
        self.steam = None
        self.is_initialized = False
        self.achievements_unlocked = set()

        if STEAM_AVAILABLE:
            self._initialize_steam()

    # --------------------------------------------------------
    # Inicialização
    # --------------------------------------------------------
    def _initialize_steam(self):
        try:
            self.steam = STEAMWORKS()

            if self.steam.initialize():
                self.is_initialized = True
                print("[SteamManager] ✅ SteamworksPy inicializado")

                # Carrega achievements
                self._load_achievements()
            else:
                print("[SteamManager] ⚠️ SteamworksPy falhou ao inicializar")
                self.is_initialized = False

        except Exception as e:
            print(f"[SteamManager] ❌ Erro ao iniciar SteamworksPy: {e}")
            self.is_initialized = False

    # --------------------------------------------------------
    # Achievement Loader
    # --------------------------------------------------------
    def _load_achievements(self):
        if not self.is_initialized:
            return

        try:
            count = self.steam.UserStats.GetNumAchievements()
            print(f"[SteamManager] Total de achievements no Steam: {count}")

            for i in range(count):
                name = self.steam.UserStats.GetAchievementName(i)
                achieved = self.steam.UserStats.GetAchievement(name)

                if achieved:
                    self.achievements_unlocked.add(name)

            print(f"[SteamManager] {len(self.achievements_unlocked)} achievements carregados")

        except Exception as e:
            print(f"[SteamManager] Erro ao carregar achievements: {e}")

    # --------------------------------------------------------
    # Achievement
    # --------------------------------------------------------
    def unlock_achievement(self, achievement_id: str):
        if not self.is_initialized:
            print(f"[SteamManager] (offline) achievement simulado: {achievement_id}")
            return False

        if achievement_id in self.achievements_unlocked:
            return False

        try:
            # SteamworksPy usa: SetAchievement("ID")
            if self.steam.UserStats.SetAchievement(achievement_id):
                self.steam.UserStats.StoreStats()
                self.achievements_unlocked.add(achievement_id)
                print(f"[SteamManager] 🏆 Achievement desbloqueado: {achievement_id}")
                return True

            print(f"[SteamManager] ⚠️ Falha ao desbloquear achievement: {achievement_id}")
            return False

        except Exception as e:
            print(f"[SteamManager] Erro ao desbloquear achievement: {e}")
            return False

    # --------------------------------------------------------
    # Stats
    # --------------------------------------------------------
    def set_stat(self, stat_name: str, value: int):
        if not self.is_initialized:
            return False

        try:
            if self.steam.UserStats.SetStat(stat_name, int(value)):
                self.steam.UserStats.StoreStats()
                print(f"[SteamManager] 📊 Stat {stat_name} = {value}")
                return True

            print(f"[SteamManager] ⚠️ Falha ao atualizar stat: {stat_name}")
            return False

        except Exception as e:
            print(f"[SteamManager] Erro ao atualizar stat: {e}")
            return False

    def get_stat(self, stat_name: str):
        if not self.is_initialized:
            return 0

        try:
            return self.steam.UserStats.GetStatInt(stat_name)
        except:
            return 0

    # --------------------------------------------------------
    # Callback Loop
    # --------------------------------------------------------
    def run_callbacks(self):
        if self.is_initialized:
            self.steam.RunCallbacks()

    # --------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------
    def shutdown(self):
        print("[SteamManager] Finalizando SteamworksPy…")
        # SteamworksPy não tem Shutdown (Steam faz sozinho)
        return

    # --------------------------------------------------------
    # Integrado ao jogo
    # --------------------------------------------------------
    def on_quest_resolved(self, quest, heroes, result):
        # --- Atualiza stats ---
        if result == "success":
            total = self.get_stat(Stats.QUESTS_COMPLETED) + 1
            self.set_stat(Stats.QUESTS_COMPLETED, total)

            # Achievements de número de quests
            match total:
                case 1:
                    self.unlock_achievement(Achievements.FIRST_QUEST)
                case 10:
                    self.unlock_achievement(Achievements.COMPLETE_10_QUESTS)
                case 50:
                    self.unlock_achievement(Achievements.COMPLETE_50_QUESTS)
                case 100:
                    self.unlock_achievement(Achievements.COMPLETE_100_QUESTS)

        elif result == "failure":
            total = self.get_stat(Stats.QUESTS_FAILED) + 1
            self.set_stat(Stats.QUESTS_FAILED, total)

        # --- Críticos ---
        if result == "critical_success":
            self.unlock_achievement(Achievements.CRITICAL_SUCCESS)
        if result == "critical_failure":
            self.unlock_achievement(Achievements.CRITICAL_FAILURE)


        # --- Achievements de heróis ---
        for hero in heroes:
            levels_to_check = [5, 10]
            for lvl in levels_to_check:
                achievement = f"HERO_{hero.id}_LEVEL_{lvl}"
                if hero.level >= lvl:
                    self.unlock_achievement(achievement)


        # --- Achievements específicos de quests ---
        if hasattr(quest, "achievement") and quest.achievement:
            self.unlock_achievement(quest.achievement)

        self._check_hidden_events(quest, heroes, result)

    # --------------------------------------------------------
    # Eventos especiais escondidos
    # --------------------------------------------------------
    def _check_hidden_events(self, quest, heroes, result):
        if quest.id == 41:
            for hero in heroes:
                if hero.id == "1":
                    self.unlock_achievement("QUEST_41_WITH_LYRA")


# Singleton
_steam_manager = None

def get_steam_manager():
    global _steam_manager
    if _steam_manager is None:
        _steam_manager = SteamManager()
    return _steam_manager


# ============================================
# Achievements
# ============================================
class Achievements:
    FIRST_QUEST = "FIRST_QUEST"
    COMPLETE_10_QUESTS = "COMPLETE_10_QUESTS"
    COMPLETE_50_QUESTS = "COMPLETE_50_QUESTS"
    COMPLETE_100_QUESTS = "COMPLETE_100_QUESTS"

    CRITICAL_SUCCESS = "CRITICAL_SUCCESS"
    CRITICAL_FAILURE = "CRITICAL_FAILURE"


    QUESTS_COMPLETED = "QUESTS_COMPLETED"
    QUESTS_FAILED = "QUESTS_FAILED"
    HEROES_RECRUITED = "HEROES_RECRUITED"
    TOTAL_TURNS_PLAYED = "TOTAL_TURNS_PLAYED"
    TOTAL_PLAYTIME = "TOTAL_PLAYTIME"
    
    # RECRUIT_FIRST_HERO = "RECRUIT_FIRST_HERO"
    # RECRUIT_5_HEROES = "RECRUIT_5_HEROES"
    # RECRUIT_ALL_HEROES = "RECRUIT_ALL_HEROES"
    
    LYRA_LEVEL_5 = "HERO_1_LEVEL_5"
    LYRA_LEVEL_10 = "HERO_1_LEVEL_10"

    # Elara
    ELARA_LEVEL_5 = "HERO_2_LEVEL_5"
    ELARA_LEVEL_10 = "HERO_2_LEVEL_10"

    # Kael
    KAEL_LEVEL_5 = "HERO_3_LEVEL_5"
    KAEL_LEVEL_10 = "HERO_3_LEVEL_10"

    # Leonardo
    LEO_LEVEL_5 = "HERO_4_LEVEL_5"
    LEO_LEVEL_10 = "HERO_4_LEVEL_10"
    
    # CRITICAL_SUCCESS = "CRITICAL_SUCCESS"
    # CRITICAL_FAILURE = "CRITICAL_FAILURE"
    
    SURVIVE_100_TURNS = "SURVIVE_100_TURNS"


# ============================================
# STATS DO JOGO
# ============================================
class Stats:
    """IDs das stats do jogo"""
    QUESTS_COMPLETED = "QUESTS_COMPLETED"
    QUESTS_FAILED = "QUESTS_FAILED"
    HEROES_RECRUITED = "HEROES_RECRUITED"
    TOTAL_TURNS_PLAYED = "TOTAL_TURNS_PLAYED"
    TOTAL_PLAYTIME = "TOTAL_PLAYTIME"