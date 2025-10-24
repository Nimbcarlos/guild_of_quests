# core/steam_manager.py
"""
Gerenciador de integração com Steam
Handles achievements, stats, and Steam features
"""

try:
    from steamworks import STEAMWORKS
    STEAM_AVAILABLE = True
except ImportError:
    print("[SteamManager] Steamworks não disponível - rodando em modo offline")
    STEAM_AVAILABLE = False


class SteamManager:
    def __init__(self):
        self.steam = None
        self.is_initialized = False
        self.achievements_unlocked = set()
        
        if STEAM_AVAILABLE:
            self._initialize_steam()
    
    def _initialize_steam(self):
        """Inicializa o Steamworks"""
        try:
            self.steam = STEAMWORKS()
            
            if self.steam.initialize():
                self.is_initialized = True
                print("[SteamManager] ✅ Steamworks inicializado com sucesso")
                print(f"[SteamManager] Usuario: {self.steam.Users.GetSteamID()}")
                self._load_achievements()
            else:
                print("[SteamManager] ⚠️ Falha ao inicializar Steamworks")
                self.is_initialized = False
                
        except Exception as e:
            print(f"[SteamManager] ❌ Erro ao inicializar Steam: {e}")
            self.is_initialized = False
    
    def _load_achievements(self):
        """Carrega achievements já desbloqueados"""
        if not self.is_initialized:
            return
        
        try:
            # Pega todos os achievements do jogo
            num_achievements = self.steam.UserStats.GetNumAchievements()
            
            for i in range(num_achievements):
                achievement_name = self.steam.UserStats.GetAchievementName(i)
                is_achieved = self.steam.UserStats.GetAchievement(achievement_name)
                
                if is_achieved:
                    self.achievements_unlocked.add(achievement_name)
            
            print(f"[SteamManager] {len(self.achievements_unlocked)} achievements desbloqueados")
            
        except Exception as e:
            print(f"[SteamManager] Erro ao carregar achievements: {e}")
    
    def unlock_achievement(self, achievement_id: str):
        """
        Desbloqueia um achievement
        
        Args:
            achievement_id: ID do achievement (ex: "FIRST_QUEST", "LEVEL_10")
        
        Returns:
            bool: True se desbloqueou com sucesso
        """
        if not self.is_initialized:
            print(f"[SteamManager] Steam não inicializado - Achievement simulado: {achievement_id}")
            return False
        
        if achievement_id in self.achievements_unlocked:
            print(f"[SteamManager] Achievement já desbloqueado: {achievement_id}")
            return False
        
        try:
            # Desbloqueia o achievement
            success = self.steam.UserStats.SetAchievement(achievement_id)
            
            if success:
                # Salva no Steam
                self.steam.UserStats.StoreStats()
                self.achievements_unlocked.add(achievement_id)
                print(f"[SteamManager] 🏆 Achievement desbloqueado: {achievement_id}")
                return True
            else:
                print(f"[SteamManager] ⚠️ Falha ao desbloquear achievement: {achievement_id}")
                return False
                
        except Exception as e:
            print(f"[SteamManager] ❌ Erro ao desbloquear achievement: {e}")
            return False
    
    def set_stat(self, stat_name: str, value: int):
        """
        Atualiza uma estatística no Steam
        
        Args:
            stat_name: Nome da stat (ex: "QUESTS_COMPLETED", "HEROES_RECRUITED")
            value: Valor da stat
        """
        if not self.is_initialized:
            return False
        
        try:
            self.steam.UserStats.SetStat(stat_name, value)
            self.steam.UserStats.StoreStats()
            print(f"[SteamManager] 📊 Stat atualizada: {stat_name} = {value}")
            return True
        except Exception as e:
            print(f"[SteamManager] Erro ao atualizar stat: {e}")
            return False
    
    def get_stat(self, stat_name: str) -> int:
        """
        Pega o valor de uma estatística
        
        Args:
            stat_name: Nome da stat
        
        Returns:
            int: Valor da stat ou 0 se não encontrada
        """
        if not self.is_initialized:
            return 0
        
        try:
            return self.steam.UserStats.GetStat(stat_name)
        except:
            return 0
    
    def is_achievement_unlocked(self, achievement_id: str) -> bool:
        """Verifica se um achievement foi desbloqueado"""
        return achievement_id in self.achievements_unlocked
    
    def run_callbacks(self):
        """
        Processa callbacks do Steam
        Deve ser chamado regularmente (a cada frame ou a cada X segundos)
        """
        if self.is_initialized and self.steam:
            self.steam.run_callbacks()
    
    def shutdown(self):
        """Desliga o Steamworks"""
        if self.is_initialized and self.steam:
            print("[SteamManager] Desligando Steamworks...")
            self.steam.shutdown()


# Singleton global
_steam_manager = None

def get_steam_manager():
    """Retorna a instância global do SteamManager"""
    global _steam_manager
    if _steam_manager is None:
        _steam_manager = SteamManager()
    return _steam_manager


# ============================================
# ACHIEVEMENTS DO JOGO
# ============================================
class Achievements:
    """IDs dos achievements do jogo"""
    FIRST_QUEST = "FIRST_QUEST"
    COMPLETE_10_QUESTS = "COMPLETE_10_QUESTS"
    COMPLETE_50_QUESTS = "COMPLETE_50_QUESTS"
    COMPLETE_100_QUESTS = "COMPLETE_100_QUESTS"
    
    RECRUIT_FIRST_HERO = "RECRUIT_FIRST_HERO"
    RECRUIT_5_HEROES = "RECRUIT_5_HEROES"
    RECRUIT_ALL_HEROES = "RECRUIT_ALL_HEROES"
    
    HERO_LEVEL_5 = "HERO_LEVEL_5"
    HERO_LEVEL_10 = "HERO_LEVEL_10"
    HERO_MAX_LEVEL = "HERO_MAX_LEVEL"
    
    CRITICAL_SUCCESS = "CRITICAL_SUCCESS"
    CRITICAL_FAILURE = "CRITICAL_FAILURE"
    
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
