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

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.lang import Builder

KV = """
<NotificationLabel>:
    size_hint: None, None
    size: self.texture_size[0] + dp(20), self.texture_size[1] + dp(10)
    canvas.before:
        Color:
            rgba: 0.2, 0.2, 0.2, 0.8 # Semi-transparent dark background
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(5),]

<MyApp>:
    FloatLayout:
        id: notification_area
        # Other widgets for your main application can go here
        Button:
            text: "Show Notification"
            size_hint: None, None
            size: dp(150), dp(50)
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            on_release: app.show_notification("Hello from Kivy!")
"""

class NotificationLabel(Label):
    pass

class MyApp(App):
    def build(self):
        return Builder.load_string(KV)

    def show_notification(self, message):
        notification_label = NotificationLabel(text=message)
        notification_area = self.root.ids.notification_area

        # Position the notification
        notification_label.pos_hint = {'center_x': 0.5, 'top': 0.9}
        notification_label.opacity = 0 # Start invisible for animation

        notification_area.add_widget(notification_label)

        # Animate appearance
        anim_in = Animation(opacity=1, y=notification_label.y - dp(20), duration=0.3)
        anim_in.start(notification_label)

        # Schedule removal after a delay
        Clock.schedule_once(lambda dt: self.hide_notification(notification_label), 3)

    def hide_notification(self, notification_label):
        anim_out = Animation(opacity=0, y=notification_label.y + dp(20), duration=0.3)
        anim_out.bind(on_complete=lambda *args: self.root.ids.notification_area.remove_widget(notification_label))
        anim_out.start(notification_label)

if __name__ == '__main__':
    MyApp().run()