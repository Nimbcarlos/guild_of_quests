# screens/settings_screen.py - CustomTkinter version
import json
import os
import customtkinter as ctk

CONFIG_FILE = "config.json"


class SettingsScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Configurações padrão
        self.music_muted = False
        self.ui_muted = False
        self.music_volume = 1.0
        self.ui_volume = 1.0
        self.current_language = "pt"
        self.screen_mode = "Janela"
        self.screen_size = [800, 600]
        self.available_sizes = [
            [800, 600],
            [1024, 768],
            [1280, 720],
            [1366, 768],
            [1920, 1080]
        ]
        
        # Carrega configurações
        self.load_config()
        
        # Constrói UI
        self.build_ui()
    
    def build_ui(self):
        """Constrói a interface de configurações"""
        # Container principal com scroll
        main_container = ctk.CTkScrollableFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_container,
            text="⚙️ Configurações",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(0, 30))
        
        # ==================== IDIOMA ====================
        lang_frame = self._create_section_frame(main_container, "🌐 Idioma")
        
        self.lang_var = ctk.StringVar(value=self.current_language)
        
        lang_options = {"Português": "pt", "English": "en", "Español": "es"}
        
        for lang_name, lang_code in lang_options.items():
            rb = ctk.CTkRadioButton(
                lang_frame,
                text=lang_name,
                variable=self.lang_var,
                value=lang_code,
                command=lambda: self.set_language(self.lang_var.get())
            )
            rb.pack(anchor="w", pady=5, padx=20)
        
        # ==================== MODO DE TELA ====================
        screen_frame = self._create_section_frame(main_container, "🖥️ Modo de Tela")
        
        self.screen_mode_var = ctk.StringVar(value=self.screen_mode)
        
        mode_options = ["Janela", "Fullscreen"]
        
        for mode in mode_options:
            rb = ctk.CTkRadioButton(
                screen_frame,
                text=mode,
                variable=self.screen_mode_var,
                value=mode,
                command=lambda: self.set_screen_mode(self.screen_mode_var.get())
            )
            rb.pack(anchor="w", pady=5, padx=20)
        
        # ==================== TAMANHO DA JANELA ====================
        size_frame = self._create_section_frame(main_container, "📐 Tamanho da Janela")
        
        self.size_var = ctk.StringVar(value=f"{self.screen_size[0]}x{self.screen_size[1]}")
        
        size_menu = ctk.CTkOptionMenu(
            size_frame,
            variable=self.size_var,
            values=[f"{w}x{h}" for w, h in self.available_sizes],
            command=self._on_size_change
        )
        size_menu.pack(pady=10, padx=20, fill="x")
        
        # ==================== VOLUME DA MÚSICA ====================
        music_frame = self._create_section_frame(main_container, "🎵 Volume da Música")
        
        music_controls = ctk.CTkFrame(music_frame, fg_color="transparent")
        music_controls.pack(fill="x", padx=20, pady=10)
        
        self.music_slider = ctk.CTkSlider(
            music_controls,
            from_=0,
            to=1,
            number_of_steps=100,
            command=self.set_music_volume
        )
        self.music_slider.set(self.music_volume)
        self.music_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.music_volume_label = ctk.CTkLabel(
            music_controls,
            text=f"{int(self.music_volume * 100)}%",
            width=50
        )
        self.music_volume_label.pack(side="left")
        
        self.music_mute_var = ctk.BooleanVar(value=self.music_muted)
        self.music_mute_check = ctk.CTkCheckBox(
            music_frame,
            text="Mutar Música",
            variable=self.music_mute_var,
            command=lambda: self.set_music_mute(self.music_mute_var.get())
        )
        self.music_mute_check.pack(anchor="w", padx=20, pady=5)
        
        # ==================== VOLUME DA UI ====================
        ui_frame = self._create_section_frame(main_container, "🔊 Volume da Interface")
        
        ui_controls = ctk.CTkFrame(ui_frame, fg_color="transparent")
        ui_controls.pack(fill="x", padx=20, pady=10)
        
        self.ui_slider = ctk.CTkSlider(
            ui_controls,
            from_=0,
            to=1,
            number_of_steps=100,
            command=self.set_ui_volume
        )
        self.ui_slider.set(self.ui_volume)
        self.ui_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.ui_volume_label = ctk.CTkLabel(
            ui_controls,
            text=f"{int(self.ui_volume * 100)}%",
            width=50
        )
        self.ui_volume_label.pack(side="left")
        
        self.ui_mute_var = ctk.BooleanVar(value=self.ui_muted)
        self.ui_mute_check = ctk.CTkCheckBox(
            ui_frame,
            text="Mutar Sons da Interface",
            variable=self.ui_mute_var,
            command=lambda: self.set_ui_mute(self.ui_mute_var.get())
        )
        self.ui_mute_check.pack(anchor="w", padx=20, pady=5)
        
        # ==================== BOTÕES ====================
        btn_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Salvar e Voltar",
            command=self.save_and_return,
            width=200,
            height=50,
            font=ctk.CTkFont(size=14)
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancelar",
            command=self.cancel,
            width=200,
            height=50,
            font=ctk.CTkFont(size=14),
            fg_color="gray40",
            hover_color="gray30"
        )
        cancel_btn.pack(side="left", padx=10)
    
    def _create_section_frame(self, parent, title):
        """Cria um frame de seção com título"""
        section = ctk.CTkFrame(parent)
        section.pack(fill="x", pady=10)
        
        title_label = ctk.CTkLabel(
            section,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=10, pady=(10, 5))
        
        return section
    
    def _on_size_change(self, value):
        """Callback quando o tamanho da janela muda"""
        w, h = map(int, value.split("x"))
        self.set_screen_size([w, h])
    
    # ==================== CONFIG LOAD/SAVE ====================
    def load_config(self):
        """Carrega configurações do arquivo JSON"""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.current_language = data.get("language", "pt")
                    self.screen_mode = data.get("screen_mode", "Janela")
                    self.screen_size = data.get("screen_size", [800, 600])
                    self.music_muted = data.get("music_muted", False)
                    self.ui_muted = data.get("ui_muted", False)
                    self.music_volume = data.get("music_volume", 1.0)
                    self.ui_volume = data.get("ui_volume", 1.0)
                    
                    # Aplica configurações na janela
                    self._apply_window_settings()
            except Exception as e:
                print(f"Erro ao carregar config: {e}")
                self.save_config()
        else:
            self.save_config()
    
    def save_config(self):
        """Salva configurações no arquivo JSON"""
        data = {
            "language": self.current_language,
            "screen_mode": self.screen_mode,
            "screen_size": self.screen_size,
            "music_muted": self.music_muted,
            "ui_muted": self.ui_muted,
            "music_volume": self.music_volume,
            "ui_volume": self.ui_volume
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f, indent=4)
            print("✅ Configurações salvas")
        except Exception as e:
            print(f"❌ Erro ao salvar config: {e}")
    
    def _apply_window_settings(self):
        """Aplica as configurações de janela"""
        try:
            self.app.geometry(f"{self.screen_size[0]}x{self.screen_size[1]}")
            
            if self.screen_mode == "Fullscreen":
                self.app.attributes('-fullscreen', True)
            else:
                self.app.attributes('-fullscreen', False)
        except Exception as e:
            print(f"Erro ao aplicar configurações de janela: {e}")
    
    # ==================== SETTERS ====================
    def set_language(self, lang):
        """Define o idioma"""
        self.current_language = lang
        print(f"Idioma definido para {lang}")
        self.save_config()
    
    def set_screen_mode(self, mode):
        """Define o modo de tela"""
        self.screen_mode = mode
        
        if mode == "Fullscreen":
            self.app.attributes('-fullscreen', True)
        else:
            self.app.attributes('-fullscreen', False)
        
        print(f"Tela: {mode}")
        self.save_config()
    
    def set_screen_size(self, size):
        """Define o tamanho da janela"""
        self.screen_size = size
        self.app.geometry(f"{size[0]}x{size[1]}")
        print(f"Tamanho da tela definido para {size[0]}x{size[1]}")
        self.save_config()
    
    def set_music_volume(self, value):
        """Define o volume da música"""
        self.music_volume = float(value)
        self.music_volume_label.configure(text=f"{int(self.music_volume * 100)}%")
        print(f"Volume música: {self.music_volume}")
        # Auto-save pode ser desabilitado se preferir salvar só no botão
        # self.save_config()
    
    def set_ui_volume(self, value):
        """Define o volume da UI"""
        self.ui_volume = float(value)
        self.ui_volume_label.configure(text=f"{int(self.ui_volume * 100)}%")
        print(f"Volume UI: {self.ui_volume}")
        # Auto-save pode ser desabilitado se preferir salvar só no botão
        # self.save_config()
    
    def set_music_mute(self, value: bool):
        """Muta/desmuta música"""
        self.music_muted = value
        print(f"Música mute: {value}")
        self.save_config()
    
    def set_ui_mute(self, value: bool):
        """Muta/desmuta sons da interface"""
        self.ui_muted = value
        print(f"UI mute: {value}")
        self.save_config()
    
    def save_and_return(self):
        """Salva configurações e volta ao menu"""
        self.save_config()
        self.app.show_screen("menu")
    
    def cancel(self):
        """Cancela alterações e volta ao menu"""
        self.load_config()  # Recarrega config original
        self.app.show_screen("menu")