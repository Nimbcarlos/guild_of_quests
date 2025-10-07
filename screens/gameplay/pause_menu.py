# screens/gameplay/pause_menu.py
import customtkinter as ctk


class PauseMenu:
    """Menu de pausa sobreposto na tela"""
    
    def __init__(self, parent, language_manager, app):
        self.parent = parent
        self.lm = language_manager
        self.app = app
        self.overlay = None
        self.on_save_callback = None
    
    def show(self, on_save_callback=None):
        """Mostra o menu de pausa"""
        if self.overlay:
            self.hide()
            return
        
        self.on_save_callback = on_save_callback
        
        # Overlay semi-transparente de fundo
        self.overlay = ctk.CTkFrame(
            self.parent,
            fg_color=("#000000", "#000000"),
            width=1200,
            height=800
        )
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Frame do menu centralizado
        menu_frame = ctk.CTkFrame(
            self.overlay,
            width=350,
            height=450,
            corner_radius=15,
            border_width=2,
            border_color=("#666666", "#444444")
        )
        menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title_label = ctk.CTkLabel(
            menu_frame,
            text=f"⏸️ {self.lm.t('pause_menu_title')}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        btn_config = {"width": 280, "height": 50, "font": ctk.CTkFont(size=14)}
        
        # Continuar (fecha o menu)
        ctk.CTkButton(
            menu_frame,
            text="▶️ Continuar",
            command=self.hide,
            fg_color="#2e7d32",
            hover_color="#1b5e20",
            **btn_config
        ).pack(pady=8)
        
        # Salvar
        ctk.CTkButton(
            menu_frame,
            text=f"💾 {self.lm.t('save_game')}",
            command=self._on_save_click,
            **btn_config
        ).pack(pady=8)
        
        # Carregar
        ctk.CTkButton(
            menu_frame,
            text=f"📂 {self.lm.t('load_game')}",
            command=self._on_load_click,
            **btn_config
        ).pack(pady=8)
        
        # Menu
        ctk.CTkButton(
            menu_frame,
            text=f"🏠 {self.lm.t('back_to_menu')}",
            command=self._on_menu_click,
            fg_color="gray40",
            hover_color="gray30",
            **btn_config
        ).pack(pady=8)
        
        # Sair
        ctk.CTkButton(
            menu_frame,
            text=f"🚪 {self.lm.t('quit_game')}",
            command=self.app.quit,
            fg_color="#d32f2f",
            hover_color="#b71c1c",
            **btn_config
        ).pack(pady=8)
        
        # Bind ESC para fechar o menu
        self.overlay.bind("<Escape>", lambda e: self.hide())
        self.overlay.focus_set()
    
    def hide(self):
        """Fecha o menu de pausa"""
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None
    
    def _on_save_click(self):
        """Handler do botão Salvar"""
        self.hide()
        if self.on_save_callback:
            self.on_save_callback()
    
    def _on_load_click(self):
        """Handler do botão Carregar"""
        self.hide()
        self.app.show_screen("loadgame")
    
    def _on_menu_click(self):
        """Handler do botão Menu"""
        self.hide()
        self.app.show_screen("menu")