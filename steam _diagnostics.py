# ════════════════════════════════════════════════════════════════
# 🔍 STEAM DIAGNOSTICS TOOL
# ════════════════════════════════════════════════════════════════
#
# Execute este arquivo para diagnosticar problemas com Steam
# python steam_diagnostics.py
#
# ════════════════════════════════════════════════════════════════

import os
import platform
import sys

def check_steam_files():
    """Verifica se os arquivos necessários existem."""
    print("=" * 60)
    print("1️⃣  VERIFICANDO ARQUIVOS")
    print("=" * 60)
    
    required_files = {
        "steam_appid.txt": "Arquivo com App ID do Steam",
        "steam_api64.dll": "DLL do Steam (64-bit)",
        "steam_api.dll": "DLL do Steam (32-bit)",
    }
    
    all_ok = True
    
    for filename, description in required_files.items():
        exists = os.path.exists(filename)
        status = "✅" if exists else "❌"
        print(f"  {status} {filename:20s} - {description}")
        
        if not exists and "steam_appid" in filename:
            print(f"      → Criar arquivo 'steam_appid.txt' com conteúdo: 480")
            all_ok = False
        
        if not exists and ".dll" in filename:
            if platform.architecture()[0] == '64bit' and "64" in filename:
                print(f"      → CRÍTICO: Baixe steam_api64.dll do Steamworks SDK")
                all_ok = False
    
    if os.path.exists("steam_appid.txt"):
        with open("steam_appid.txt", "r") as f:
            app_id = f.read().strip()
            print(f"\n  📝 Conteúdo do steam_appid.txt: '{app_id}'")
            if app_id != "480":
                print(f"      ⚠️  Para testes, use '480' (Spacewar)")
    
    return all_ok


def check_steam_running():
    """Verifica se o Steam está rodando."""
    print("\n" + "=" * 60)
    print("2️⃣  VERIFICANDO SE STEAM ESTÁ RODANDO")
    print("=" * 60)
    
    import subprocess
    
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                ['tasklist', '/FI', 'IMAGENAME eq steam.exe'],
                capture_output=True,
                text=True
            )
            running = "steam.exe" in result.stdout.lower()
        
        else:  # Linux/Mac
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            running = "steam" in result.stdout.lower()
        
        if running:
            print("  ✅ Steam está rodando")
            return True
        else:
            print("  ❌ Steam NÃO está rodando")
            print("      → Abra o Steam antes de rodar o jogo")
            return False
    
    except Exception as e:
        print(f"  ⚠️  Não foi possível verificar: {e}")
        return False


def check_python_architecture():
    """Verifica a arquitetura do Python."""
    print("\n" + "=" * 60)
    print("3️⃣  VERIFICANDO PYTHON")
    print("=" * 60)
    
    arch = platform.architecture()[0]
    py_version = sys.version.split()[0]
    
    print(f"  📊 Python: {py_version}")
    print(f"  📊 Arquitetura: {arch}")
    
    if arch == '64bit':
        print(f"  ✅ Python 64-bit detectado")
        print(f"      → Usar steam_api64.dll")
        return "steam_api64.dll"
    else:
        print(f"  ✅ Python 32-bit detectado")
        print(f"      → Usar steam_api.dll")
        return "steam_api.dll"


def test_steam_api_loading():
    """Testa se consegue carregar a DLL."""
    print("\n" + "=" * 60)
    print("4️⃣  TESTANDO CARREGAMENTO DA DLL")
    print("=" * 60)
    
    import ctypes
    
    arch = platform.architecture()[0]
    if arch == '64bit':
        dll_name = "steam_api64.dll"
    else:
        dll_name = "steam_api.dll"
    
    if not os.path.exists(dll_name):
        print(f"  ❌ {dll_name} não encontrada!")
        return False
    
    try:
        print(f"  🔄 Tentando carregar {dll_name}...")
        
        # Adiciona diretório ao PATH
        current_dir = os.path.abspath(os.getcwd())
        os.environ['PATH'] = current_dir + os.pathsep + os.environ.get('PATH', '')
        
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(current_dir)
        
        # Tenta carregar
        dll = ctypes.CDLL(dll_name, winmode=0)
        print(f"  ✅ {dll_name} carregada com sucesso!")
        
        # Testa se tem a função SteamAPI_Init
        try:
            init_func = dll.SteamAPI_Init
            print(f"  ✅ Função SteamAPI_Init encontrada")
            return True
        except AttributeError:
            print(f"  ❌ Função SteamAPI_Init NÃO encontrada na DLL")
            return False
    
    except Exception as e:
        print(f"  ❌ Erro ao carregar DLL: {e}")
        print(f"\n  Possíveis causas:")
        print(f"    1. DLL corrompida (baixe novamente do Steamworks SDK)")
        print(f"    2. Faltando dependências (instale Visual C++ Redistributable)")
        print(f"    3. Versão errada da DLL (32-bit vs 64-bit)")
        return False


def test_steam_initialization():
    """Testa se consegue inicializar o Steam."""
    print("\n" + "=" * 60)
    print("5️⃣  TESTANDO INICIALIZAÇÃO DO STEAM")
    print("=" * 60)
    
    try:
        # Importa o steamworks customizado
        from core.steamworks_wrapper import STEAMWORKS
        
        print("  🔄 Criando instância STEAMWORKS...")
        steam = STEAMWORKS()
        
        print("  🔄 Inicializando Steam...")
        if steam.initialize():
            print("  ✅ Steam inicializado com SUCESSO!")
            
            # Testa obter Steam ID
            try:
                steam_id = steam.Users.GetSteamID(steam)
                print(f"  ✅ Steam ID: {steam_id}")
            except Exception as e:
                print(f"  ⚠️  Não conseguiu obter Steam ID: {e}")
            
            # Limpa
            steam.shutdown()
            return True
        else:
            print("  ❌ Falha ao inicializar Steam")
            print("\n  Verifique:")
            print("    1. Steam está rodando?")
            print("    2. Você está logado no Steam?")
            print("    3. steam_appid.txt existe com '480'?")
            return False
    
    except ImportError as e:
        print(f"  ❌ Erro ao importar steamworks.py: {e}")
        print(f"      → Verifique se steamworks.py existe na pasta")
        return False
    except Exception as e:
        print(f"  ❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_achievement():
    """Testa desbloquear um achievement."""
    print("\n" + "=" * 60)
    print("6️⃣  TESTANDO ACHIEVEMENT")
    print("=" * 60)
    
    try:
        from steamworks import STEAMWORKS
        
        steam = STEAMWORKS()
        
        if not steam.initialize():
            print("  ❌ Não foi possível inicializar Steam")
            return False
        
        print("  🔄 Tentando desbloquear achievement de teste...")
        
        # Tenta desbloquear achievement
        test_ach = "ACH_WIN_ONE_GAME"  # Achievement padrão do Spacewar (480)
        
        result = steam.UserStats.SetAchievement(steam, test_ach)
        
        if result:
            print(f"  ✅ SetAchievement retornou True")
            
            # Tenta salvar
            if steam.UserStats.StoreStats(steam):
                print(f"  ✅ StoreStats retornou True")
                print(f"\n  🎉 Achievement '{test_ach}' desbloqueado!")
                print(f"      Verifique no Steam se apareceu")
            else:
                print(f"  ❌ StoreStats retornou False")
        else:
            print(f"  ❌ SetAchievement retornou False")
            print(f"\n  Possíveis causas:")
            print(f"    1. Achievement já estava desbloqueado")
            print(f"    2. Achievement ID inválido")
            print(f"    3. Steam não está conectado")
        
        steam.shutdown()
        return result
    
    except Exception as e:
        print(f"  ❌ Erro ao testar achievement: {e}")
        import traceback
        traceback.print_exc()
        return False


def generate_report():
    """Gera relatório completo."""
    print("\n" + "=" * 60)
    print("📋 RELATÓRIO FINAL")
    print("=" * 60)
    
    print("\nResumo dos checks:")
    
    files_ok = check_steam_files()
    steam_running = check_steam_running()
    dll_name = check_python_architecture()
    dll_ok = test_steam_api_loading()
    init_ok = test_steam_initialization()
    ach_ok = test_achievement()
    
    print("\n" + "=" * 60)
    print("RESULTADO:")
    print("=" * 60)
    
    all_ok = all([files_ok, steam_running, dll_ok, init_ok])
    
    if all_ok:
        print("  ✅ TUDO OK! Achievements devem funcionar!")
    else:
        print("  ❌ Há problemas a resolver:")
        if not files_ok:
            print("      • Arquivos faltando")
        if not steam_running:
            print("      • Steam não está rodando")
        if not dll_ok:
            print("      • Problema ao carregar DLL")
        if not init_ok:
            print("      • Falha ao inicializar Steam")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n")
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       🔍 STEAM ACHIEVEMENTS DIAGNOSTICS TOOL          ║")
    print("╚═══════════════════════════════════════════════════════╝")
    print("\n")
    
    generate_report()
    
    print("\n\nPressione Enter para sair...")
    input()