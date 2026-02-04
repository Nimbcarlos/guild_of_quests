from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from core.language_manager import LanguageManager  # ✅ IMPORT DIRETO


class ConfirmationPopup(Popup):
    def __init__(self, message_key, on_confirm=None, on_cancel=None, 
                 title_key="exit_confirm_title", 
                 confirm_key="exit_confirm_yes", 
                 cancel_key="exit_confirm_no", **kwargs):
        """
        Popup de confirmação com tradução automática.
        
        Args:
            message_key: Chave de tradução da mensagem (ex: "exit_confirm_message")
            on_confirm: Callback quando confirmar
            on_cancel: Callback quando cancelar
            title_key: Chave de tradução do título (padrão: "exit_confirm_title")
            confirm_key: Chave de tradução do botão SIM (padrão: "exit_confirm_yes")
            cancel_key: Chave de tradução do botão NÃO (padrão: "exit_confirm_no")
        """
        super().__init__(**kwargs)
        
        # ✅ Instancia o LanguageManager internamente
        self.lm = LanguageManager()
        
        # ✅ Busca as traduções automaticamente
        self.title = self.lm.t(title_key)
        message = self.lm.t(message_key)
        confirm_text = self.lm.t(confirm_key)
        cancel_text = self.lm.t(cancel_key)
        
        self.size_hint = (None, None)
        self.size = (500, 250)
        self.auto_dismiss = False
        
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        
        # Layout principal
        main_layout = BoxLayout(orientation="vertical", padding=20, spacing=15)
        
        # ═══════════════════════════════════════════════════════
        # Background do popup
        # ═══════════════════════════════════════════════════════
        with main_layout.canvas.before:
            Color(0.2, 0.2, 0.2, 0.95)
            self.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        
        main_layout.bind(
            size=self._update_bg,
            pos=self._update_bg
        )
        
        # ═══════════════════════════════════════════════════════
        # Mensagem
        # ═══════════════════════════════════════════════════════
        message_label = Label(
            text=message,
            size_hint_y=0.6,
            halign="center",
            valign="middle",
            font_size="18sp",
            color=(1, 1, 1, 1)
        )
        message_label.bind(size=message_label.setter('text_size'))
        main_layout.add_widget(message_label)
        
        # ═══════════════════════════════════════════════════════
        # Botões
        # ═══════════════════════════════════════════════════════
        buttons_layout = BoxLayout(
            orientation="horizontal",
            spacing=20,
            size_hint_y=0.4,
            padding=[50, 0, 50, 0]
        )
        
        # Botão NÃO (Cancelar)
        cancel_btn = Button(
            text=cancel_text,
            size_hint=(0.5, 1),
            background_color=(0.7, 0.2, 0.2, 1),
            font_size="16sp",
            bold=True
        )
        cancel_btn.bind(on_release=self._on_cancel)
        buttons_layout.add_widget(cancel_btn)
        
        # Botão SIM (Confirmar)
        confirm_btn = Button(
            text=confirm_text,
            size_hint=(0.5, 1),
            background_color=(0.2, 0.7, 0.2, 1),
            font_size="16sp",
            bold=True
        )
        confirm_btn.bind(on_release=self._on_confirm)
        buttons_layout.add_widget(confirm_btn)
        
        main_layout.add_widget(buttons_layout)
        
        self.content = main_layout
    
    def _update_bg(self, instance, value):
        """Atualiza o background do popup."""
        self.bg_rect.size = instance.size
        self.bg_rect.pos = instance.pos
    
    def _on_confirm(self, *args):
        """Handler do botão de confirmação."""
        self.dismiss()
        if self.on_confirm:
            self.on_confirm()
    
    def _on_cancel(self, *args):
        """Handler do botão de cancelamento."""
        self.dismiss()
        if self.on_cancel:
            self.on_cancel()