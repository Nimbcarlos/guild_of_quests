# screens/load_game_screen.py - CustomTkinter version
import os
import json
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox
import core.save_manager as save

SAVE_DIR = "saves"


class LoadGameScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.build_ui()
    
    def on_show(self):
        """Callback quando a tela é mostrada"""
        self.refresh_saves()
    
    def build_ui(self):
        """Constrói a interface de carregar jogo"""
        # Container principal
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="💾 Carregar Jogo",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Frame scrollável para lista de saves
        self.saves_frame = ctk.CTkScrollableFrame(
            main_frame,
            label_text="Saves Disponíveis"
        )
        self.saves_frame.pack(fill="both", expand=True, pady=10)
        
        # Botões inferiores
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="🔄 Atualizar Lista",
            command=self.refresh_saves,
            width=150,
            height=40
        )
        refresh_btn.pack(side="left", padx=5)
        
        back_btn = ctk.CTkButton(
            btn_frame,
            text="⬅️ Voltar",
            command=lambda: self.app.show_screen("menu"),
            width=150,
            height=40,
            fg_color="gray40",
            hover_color="gray30"
        )
        back_btn.pack(side="left", padx=5)
    
    def refresh_saves(self):
        """Atualiza a lista de saves"""
        # Limpa lista atual
        for widget in self.saves_frame.winfo_children():
            widget.destroy()
        
        # Cria diretório se não existir
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)
        
        # Lista arquivos de save
        files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        
        if not files:
            no_save_label = ctk.CTkLabel(
                self.saves_frame,
                text="📂 Nenhum save encontrado",
                font=ctk.CTkFont(size=16)
            )
            no_save_label.pack(pady=50)
            return
        
        # Ordena por data de modificação (mais recente primeiro)
        files.sort(
            key=lambda f: os.path.getmtime(os.path.join(SAVE_DIR, f)),
            reverse=True
        )
        
        # Cria entradas para cada save
        for f in files:
            self._create_save_entry(f)
    
    def _create_save_entry(self, filename):
        """Cria uma entrada para um arquivo de save"""
        filepath = os.path.join(SAVE_DIR, filename)
        
        # Pega informações do save
        try:
            modified = datetime.fromtimestamp(os.path.getmtime(filepath))
            date_str = modified.strftime("%d/%m/%Y %H:%M")
            
            # Tenta ler informações adicionais do save (opcional)
            save_info = self._get_save_info(filepath)
        except Exception as e:
            print(f"Erro ao ler save {filename}: {e}")
            date_str = "Data desconhecida"
            save_info = {}
        
        # Container para este save
        save_frame = ctk.CTkFrame(self.saves_frame)
        save_frame.pack(fill="x", pady=5, padx=5)
        
        # Grid layout
        save_frame.grid_columnconfigure(0, weight=1)  # Nome e info
        save_frame.grid_columnconfigure(1, weight=0)  # Botão carregar
        save_frame.grid_columnconfigure(2, weight=0)  # Botão deletar
        
        # Info do save (nome + detalhes)
        info_frame = ctk.CTkFrame(save_frame, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Nome do save
        name_label = ctk.CTkLabel(
            info_frame,
            text=filename.replace('.json', ''),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Data de modificação
        date_label = ctk.CTkLabel(
            info_frame,
            text=f"📅 {date_str}",
            font=ctk.CTkFont(size=12),
            anchor="w",
            text_color="gray70"
        )
        date_label.pack(anchor="w")
        
        # Info adicional (turno, quests, etc.)
        if save_info:
            details = []
            if "turn" in save_info:
                details.append(f"Turno {save_info['turn']}")
            if "quests_completed" in save_info:
                details.append(f"{save_info['quests_completed']} quests completas")
            
            if details:
                details_label = ctk.CTkLabel(
                    info_frame,
                    text=" • ".join(details),
                    font=ctk.CTkFont(size=11),
                    anchor="w",
                    text_color="gray60"
                )
                details_label.pack(anchor="w")
        
        # Botão Carregar
        load_btn = ctk.CTkButton(
            save_frame,
            text="▶️ Carregar",
            command=lambda: self.load_save(filename),
            width=120,
            height=40,
            fg_color="#2e7d32",
            hover_color="#1b5e20"
        )
        load_btn.grid(row=0, column=1, padx=5)
        
        # Botão Deletar
        delete_btn = ctk.CTkButton(
            save_frame,
            text="🗑️ Apagar",
            command=lambda: self.confirm_delete(filename),
            width=100,
            height=40,
            fg_color="#c62828",
            hover_color="#b71c1c"
        )
        delete_btn.grid(row=0, column=2, padx=5)
    
    def _get_save_info(self, filepath):
        """Extrai informações do arquivo de save"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                return {
                    "turn": data.get("current_turn", "?"),
                    "quests_completed": len(data.get("completed_quests", []))
                }
        except Exception as e:
            print(f"Erro ao ler info do save: {e}")
            return {}
    
    def load_save(self, filename):
        """Carrega um save e vai para o gameplay"""
        qm = self.app.quest_manager
        
        if save.load_game(qm, filename):
            print(f"✅ Save {filename} carregado com sucesso!")
            self.app.show_screen("gameplay")
        else:
            messagebox.showerror(
                "Erro ao Carregar",
                f"Não foi possível carregar o save '{filename}'.\n"
                "O arquivo pode estar corrompido."
            )
            print(f"⚠️ Erro ao carregar {filename}")
    
    def confirm_delete(self, filename):
        """Mostra diálogo de confirmação antes de deletar"""
        result = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja apagar o save '{filename}'?\n\n"
            "Esta ação não pode ser desfeita.",
            icon="warning"
        )
        
        if result:
            self.delete_save(filename)
    
    def delete_save(self, filename):
        """Deleta um arquivo de save"""
        filepath = os.path.join(SAVE_DIR, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️ Save {filename} deletado")
                messagebox.showinfo("Sucesso", f"Save '{filename}' foi apagado.")
                self.refresh_saves()
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível apagar o save.\n\nErro: {e}"
            )
            print(f"❌ Erro ao deletar {filename}: {e}")