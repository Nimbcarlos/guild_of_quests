# screens/dialog_box.py - CustomTkinter version (In-Game Dialog)
import customtkinter as ctk
from PIL import Image, ImageTk
import random
from collections import deque
from threading import Thread
import time


class DialogueBox:
    def __init__(self, dialogue_manager, parent_screen):
        """
        dialogue_manager: instância do DialogueManager
        parent_screen: referência à tela que criou este DialogueBox
        """
        self.dm = dialogue_manager
        self.parent_screen = parent_screen
        self.dialog_frame = None  # Frame do diálogo que ficará na tela
        self.queue = deque()
        self.dialogue_label = None
        self.hero_portrait_label = None
        self.speaker_label = None
        self.dialogues = []
        self.current_index = 0
        self.char_index = 0
        self.full_text = ""
        self.typing_active = False
        self.typing_thread = None
        self.heroes = []
        self.is_visible = False
    
    def get_start_dialogues(self, hero_id: str, completed_quests):
        """
        Busca falas iniciais genéricas + específicas por quest completada
        """
        if not isinstance(completed_quests, (set, list, tuple)):
            completed_quests = set()
        
        hero_data = self.dm.start_dialogues.get("heroes", {}).get(str(hero_id), {})
        pool = []
        
        pool.extend(hero_data.get("default", []))
        
        for key, texts in hero_data.items():
            quest_id = key
            if quest_id in completed_quests:
                pool.extend(texts)
        
        if not pool:
            return None
        return random.choice(pool)
    
    def show_dialogue(self, heroes, quest_id, result: str):
        """Adiciona diálogo à fila"""
        self.queue.append((heroes, quest_id, result))
        if not self.is_visible:  # só abre se não tiver diálogo ativo
            self._process_next()
    
    def _process_next(self):
        """Processa próximo diálogo da fila"""
        if not self.queue:
            self._hide_dialog()
            return
        
        heroes, quest_id, result = self.queue.popleft()
        
        if isinstance(result, str) and quest_id == "assistant_event":
            # fala direta da assistente (não vem do dialogue_manager)
            self.dialogues = [result]
        elif result == "start":
            self.dialogues = self.dm.show_start_dialogues(heroes, quest_id)
        else:
            self.dialogues = self.dm.show_quest_dialogue(heroes, quest_id, result)
        
        if not self.dialogues:
            self.dialogues = ["..."]
        
        self.heroes = heroes
        self.current_index = 0
        self.char_index = 0
        self._show_dialog()
    
    def _show_dialog(self):
        """Mostra o frame de diálogo na tela"""
        if self.dialog_frame:
            self.dialog_frame.destroy()
        
        # Cria frame de diálogo que fica sobreposto na parte inferior
        self.dialog_frame = ctk.CTkFrame(
            self.parent_screen,
            fg_color=("#E8E8E8", "#2b2b2b"),
            border_width=2,
            border_color=("#666666", "#444444"),
            height=180  # ✅ Altura definida no construtor
        )
        
        # Posiciona na parte inferior da tela (sobreposto)
        self.dialog_frame.place(
            relx=0.5,
            rely=0.95,
            anchor="s",
            relwidth=0.95
        )
        
        # Layout interno (horizontal: portrait + texto)
        self.dialog_frame.grid_columnconfigure(0, weight=0)  # Portrait
        self.dialog_frame.grid_columnconfigure(1, weight=1)  # Texto
        self.dialog_frame.grid_rowconfigure(0, weight=1)
        
        # ==================== PORTRAIT ====================
        portrait_frame = ctk.CTkFrame(
            self.dialog_frame,
            width=140,
            fg_color="transparent"
        )
        portrait_frame.grid(row=0, column=0, sticky="nsw", padx=10, pady=10)
        portrait_frame.grid_propagate(False)
        
        self.hero_portrait_label = ctk.CTkLabel(
            portrait_frame,
            text="👤",
            font=ctk.CTkFont(size=80)
        )
        self.hero_portrait_label.pack(expand=True)
        
        # ==================== TEXTO ====================
        text_frame = ctk.CTkFrame(self.dialog_frame, fg_color="transparent")
        text_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        text_frame.grid_rowconfigure(0, weight=0)  # Speaker
        text_frame.grid_rowconfigure(1, weight=1)  # Dialogue
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Nome do falante
        self.speaker_label = ctk.CTkLabel(
            text_frame,
            text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w"
        )
        self.speaker_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # Texto do diálogo
        self.dialogue_label = ctk.CTkLabel(
            text_frame,
            text="",
            font=ctk.CTkFont(size=15),
            anchor="nw",
            justify="left",
            wraplength=700
        )
        self.dialogue_label.grid(row=1, column=0, sticky="nsew")
        
        # Indicador de "clique para continuar"
        self.continue_label = ctk.CTkLabel(
            text_frame,
            text="▼ Clique ou pressione ESPAÇO para continuar ▼",
            font=ctk.CTkFont(size=11),
            text_color="gray60",
            anchor="e"
        )
        self.continue_label.grid(row=2, column=0, sticky="e", pady=(5, 0))
        self.continue_label.grid_remove()  # Esconde inicialmente
        
        # ==================== BINDINGS ====================
        # Clique no frame avança
        self.dialog_frame.bind("<Button-1>", self._on_click_next)
        
        # Clique nos labels também avança
        self.speaker_label.bind("<Button-1>", self._on_click_next)
        self.dialogue_label.bind("<Button-1>", self._on_click_next)
        self.hero_portrait_label.bind("<Button-1>", self._on_click_next)
        
        # Teclas para avançar
        self.parent_screen.bind("<space>", self._on_click_next)
        self.parent_screen.bind("<Return>", self._on_click_next)
        
        self.is_visible = True
        self._show_current_line()
    
    def _show_current_line(self):
        """Mostra a linha atual do diálogo"""
        if self.current_index >= len(self.dialogues):
            self._hide_dialog()
            # Processa próximo diálogo da fila após um pequeno delay
            self.parent_screen.after(100, self._process_next)
            return
        
        # Esconde indicador de continuar enquanto digita
        if self.continue_label:
            self.continue_label.grid_remove()
        
        line = self.dialogues[self.current_index]
        
        self.full_text = ""
        resolved_hero = None
        
        if isinstance(line, str):
            if self.heroes:
                hero_index = self.current_index % len(self.heroes)
                resolved_hero = self.heroes[hero_index]
                self.full_text = line.strip()
            else:
                self.full_text = line.strip()
        
        elif isinstance(line, dict):
            hero_id = line.get("id")
            text = line.get("text", "")
            self.full_text = text.strip()
            resolved_hero = next((h for h in self.heroes if h.id == hero_id), None)
        
        # Atualiza portrait e nome
        if resolved_hero:
            # Tenta carregar a imagem do herói
            try:
                # TODO: Implementar carregamento de imagem real
                # img = Image.open(resolved_hero.photo_url)
                # photo = ctk.CTkImage(light_image=img, size=(120, 120))
                # self.hero_portrait_label.configure(image=photo, text="")
                self.hero_portrait_label.configure(text="🧙")
            except:
                self.hero_portrait_label.configure(text="🧙")
            
            self.speaker_label.configure(text=resolved_hero.name)
        else:
            self.hero_portrait_label.configure(text="📜")
            self.speaker_label.configure(text="Narrador")
        
        # Inicia efeito de máquina de escrever
        self.dialogue_label.configure(text="")
        self.char_index = 0
        self.typing_active = True
        self._start_typewriter_effect()
    
    def _start_typewriter_effect(self):
        """Inicia o efeito de máquina de escrever em thread separada"""
        if self.typing_thread and self.typing_thread.is_alive():
            self.typing_active = False
            self.typing_thread.join(timeout=0.1)
        
        self.typing_active = True
        self.typing_thread = Thread(target=self._typewriter_loop, daemon=True)
        self.typing_thread.start()
    
    def _typewriter_loop(self):
        """Loop do efeito de máquina de escrever"""
        while self.typing_active and self.char_index < len(self.full_text):
            if self.dialogue_label and self.dialog_frame:
                try:
                    self.parent_screen.after(0, self._update_dialogue_text)
                    time.sleep(0.03)  # Velocidade da digitação
                except:
                    break
            else:
                break
        
        self.typing_active = False
        # Mostra indicador de continuar quando terminar de digitar
        if self.continue_label:
            try:
                self.parent_screen.after(0, lambda: self.continue_label.grid())
            except:
                pass
    
    def _update_dialogue_text(self):
        """Atualiza o texto do diálogo (chamado pela thread)"""
        if self.char_index < len(self.full_text):
            current_text = self.full_text[:self.char_index + 1]
            self.dialogue_label.configure(text=current_text)
            self.char_index += 1
    
    def _on_click_next(self, event=None):
        """Handler para avançar o diálogo"""
        if not self.is_visible:
            return
        
        if self.typing_active:
            # Se ainda está digitando, completa o texto imediatamente
            self.typing_active = False
            if self.typing_thread:
                self.typing_thread.join(timeout=0.1)
            self.dialogue_label.configure(text=self.full_text)
            self.continue_label.grid()  # Mostra indicador
        else:
            # Avança para próxima linha
            self.current_index += 1
            self._show_current_line()
    
    def _hide_dialog(self):
        """Esconde o frame de diálogo"""
        self.typing_active = False
        if self.typing_thread:
            self.typing_thread.join(timeout=0.1)
        
        # Remove bindings
        try:
            self.parent_screen.unbind("<space>")
            self.parent_screen.unbind("<Return>")
        except:
            pass
        
        if self.dialog_frame:
            try:
                self.dialog_frame.destroy()
            except:
                pass
            self.dialog_frame = None
        
        self.is_visible = False
    
    def show_assistant_message(self, msg: str):
        """Mostra mensagem da assistente"""
        # Usa o sistema de diálogo existente
        self.show_dialogue([], "assistant_event", msg)