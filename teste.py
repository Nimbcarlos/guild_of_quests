# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# """
# test_steam_simple.py
# Teste mínimo para verificar comunicação com Steam
# """
# try:
#     print("=" * 50)
#     print("TESTE SIMPLES - STEAM API")
#     print("=" * 50)
#     print()

#     # 1. Verifica arquivos
#     import os

#     print("[1/4] Verificando arquivos...")
#     files = ["steam_appid.txt", "SteamworksPy64.dll", "steam_api64.dll"]
#     ok = True

#     for f in files:
#         if os.path.exists(f):
#             print(f"  ✅ {f}")
#         else:
#             print(f"  ❌ {f} - FALTANDO")
#             ok = False

#     if not ok:
#         print("\n❌ Arquivos faltando! Não é possível testar.")
#         exit(1)

#     print()

#     # 2. Importa steamworks
#     print("[2/4] Importando steamworks.py...")
#     try:
#         from steamworks import STEAMWORKS
#         print("  ✅ Importado com sucesso")
#     except Exception as e:
#         print(f"  ❌ Erro: {e}")
#         exit(1)

#     print()

#     # 3. Inicializa Steam
#     print("[3/4] Inicializando Steam...")
#     steam = STEAMWORKS()

#     if steam.initialize():
#         print("  ✅ Steam CONECTADO!")
        
#         # Pega informações básicas
#         try:
#             steam_id = steam.Users.GetSteamID(steam)
#             print(f"  👤 Steam ID: {steam_id}")
#         except:
#             print("  ⚠️  Não foi possível pegar Steam ID")
        
#     else:
#         print("  ❌ Steam NÃO CONECTADO")
#         print("  Motivos possíveis:")
#         print("    - Steam não está rodando")
#         print("    - App ID inválido")
#         print("    - DLLs incompatíveis")
#         exit(1)

#     print()

#     # 4. Teste rápido de achievement
#     print("[4/4] Testando achievement...")
#     try:
#         # Tenta desbloquear um achievement de teste
#         result = steam.UserStats.SetAchievement(steam, "TEST_ACHIEVEMENT")
        
#         if result:
#             steam.UserStats.StoreStats(steam)
#             print("  ✅ Achievement desbloqueado! (ou já estava)")
#         else:
#             print("  ⚠️  Falha ao desbloquear (achievement pode não existir)")
        
#     except Exception as e:
#         print(f"  ❌ Erro: {e}")

#     print()

#     # Finaliza
#     steam.shutdown()
#     print("=" * 50)
#     print("✅ TESTE CONCLUÍDO")
#     print("=" * 50)
# except Exception as e:
#     print(e)

import json

file_path = "data/pt/heroes.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    names = [d.get('name', 'story') for d in data if 'story' in d]
    print(names)