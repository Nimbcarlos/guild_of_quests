import customtkinter as ctk
# Removendo import de tkinter.messagebox para evitar dependências mistas.
# from tkinter import messagebox 

class QuestDetailsPanel(ctk.CTkFrame):
    def __init__(self, master, quest_manager, language_manager):
        super().__init__(master, corner_radius=12)
        self.qm = quest_manager
        self.lm = language_manager
        self.selected_quest = None
        self.selected_heroes = []

        # 🏷️ Título
        self.title_label = ctk.CTkLabel(
            self,
            text="Detalhes da Missão",
            font=("Segoe UI", 20, "bold"),
            text_color="#FFD700",
        )
        self.title_label.pack(pady=(10, 5))

        # 📜 Área de texto com a descrição da quest
        self.description_box = ctk.CTkTextbox(
            self,
            wrap="word",
            width=500,
            height=150,
            font=("Segoe UI", 14),
            fg_color="#1e1e1e",
            text_color="#ffffff",
        )
        self.description_box.pack(padx=15, pady=5, fill="both", expand=True)
        self.description_box.insert("end", "Selecione uma missão para ver os detalhes.")
        self.description_box.configure(state="disabled")

        # 👥 Área de seleção de heróis
        self.heroes_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=8)
        self.heroes_frame.pack(pady=10, fill="x", padx=10)

        self.heroes_label = ctk.CTkLabel(
            self.heroes_frame,
            text="Heróis Selecionados: Nenhum",
            font=("Segoe UI", 14, "italic"),
            text_color="#AAAAAA",
        )
        self.heroes_label.pack(pady=5)

        # 🚀 Botão de iniciar missão
        self.start_button = ctk.CTkButton(
            self,
            text="Iniciar Missão",
            command=self.start_quest,
            fg_color="#0078D7",
            hover_color="#005A9E",
            text_color="#FFFFFF",
            font=("Segoe UI", 16, "bold"),
            corner_radius=10,
        )
        self.start_button.pack(pady=15)

        # ✅ Resultado (sucesso / falha)
        self.result_label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 16, "bold"),
            text_color="#00FF7F",
        )
        self.result_label.pack(pady=(5, 15))

    # =====================================================
    # Funções públicas chamadas pelo GameplayScreen
    # =====================================================

    def display_quest(self, quest):
        """Mostra os detalhes de uma missão selecionada."""
        self.selected_quest = quest
        self.selected_heroes = []

        self.description_box.configure(state="normal")
        self.description_box.delete("1.0", "end")
        self.description_box.insert(
            "end",
            f"{quest.name}\n\n"
            f"Dificuldade: {quest.difficulty}\n"
            f"Recompensa: {quest.reward}\n\n"
            f"{quest.description}"
        )
        self.description_box.configure(state="disabled")

        self.heroes_label.configure(text="Heróis Selecionados: Nenhum")
        self.result_label.configure(text="")

    def update_hero_selection(self, selected_heroes):
        """Atualiza a lista de heróis mostrada no painel."""
        self.selected_heroes = selected_heroes
        if selected_heroes:
            names = ", ".join(hero.name for hero in selected_heroes)
            self.heroes_label.configure(text=f"Heróis Selecionados: {names}")
        else:
            self.heroes_label.configure(text="Heróis Selecionados: Nenhum")

    def start_quest(self):
        """Envia heróis para missão."""
        if not self.selected_quest:
            # Substituído messagebox por chamada ao log/assistente (melhor prática em ctk)
            print("Aviso: Selecione uma missão primeiro!") 
            # Alternativamente, chamar self.master.show_assistant_message("Selecione uma missão primeiro!")
            return

        if not self.selected_heroes:
            # Substituído messagebox por chamada ao log/assistente (melhor prática em ctk)
            print("Aviso: Selecione pelo menos um herói!")
            return

        # Chamada segura, assumindo que self.qm.start_quest(quest, heroes) existe
        result = self.qm.start_quest(self.selected_quest, self.selected_heroes) 

        # Atualiza o resultado
        if result.get("success"):
            self.result_label.configure(text="Missão Concluída com Sucesso!", text_color="#00FF7F")
        else:
            self.result_label.configure(text="Missão Falhou!", text_color="#FF5555")

        # Mostra o resultado narrativo no painel de diálogo
        # Assumindo que o master é o GameplayScreen e possui o método open_dialog
        if hasattr(self.master, "open_dialog"): 
            self.master.open_dialog(self.selected_heroes, self.selected_quest, result)

    def clear_panel(self):
        """Limpa o painel de detalhes."""
        self.selected_quest = None
        self.selected_heroes = []
        self.description_box.configure(state="normal")
        self.description_box.delete("1.0", "end")
        self.description_box.insert("end", "Selecione uma missão para ver os detalhes.")
        self.description_box.configure(state="disabled")
        self.heroes_label.configure(text="Heróis Selecionados: Nenhum")
        self.result_label.configure(text="")

    def display_quest(self, quest):
        """Mostra os detalhes de uma missão selecionada."""
        self.selected_quest = quest
        self.selected_heroes = []

        self.description_box.configure(state="normal")
        self.description_box.delete("1.0", "end")
        self.description_box.insert(
            "end",
            f"{quest.name}\n\n"
            f"Dificuldade: {quest.difficulty}\n"
            f"Recompensa: {quest.reward}\n\n"
            f"{quest.description}"
        )
        self.description_box.configure(state="disabled")
        self.heroes_label.configure(text="Heróis Selecionados: Nenhum")
        self.result_label.configure(text="")

    def update_hero_selection(self, selected_heroes):
        """Atualiza a lista de heróis mostrada no painel."""
        self.selected_heroes = selected_heroes
        if selected_heroes:
            names = ", ".join(hero.name for hero in selected_heroes)
            self.heroes_label.configure(text=f"Heróis Selecionados: {names}")
        else:
            self.heroes_label.configure(text="Heróis Selecionados: Nenhum")

    def start_quest(self):
        """Envia heróis para a quest usando o QuestManager."""
        if not self.selected_quest:
            print("Selecione uma missão primeiro!")
            return
        if not self.selected_heroes:
            print("Selecione pelo menos um herói!")
            return

        # Aqui usamos o QuestManager
        hero_ids = [hero.id for hero in self.selected_heroes]
        result = self.qm.send_heroes_on_quest(self.selected_quest.id, hero_ids)

        # Atualiza o resultado visual
        success = "sucesso" in result.lower() or "started" in result.lower()
        if success:
            self.result_label.configure(text="Missão Concluída com Sucesso!", text_color="#00FF7F")
        else:
            self.result_label.configure(text="Missão Falhou!", text_color="#FF5555")

        # Dispara diálogo via callback do GameplayScreen
        if hasattr(self.master, "open_dialog"):
            self.master.open_dialog(self.selected_heroes, self.selected_quest, result)

    def clear_panel(self):
        """Limpa o painel de detalhes."""
        self.selected_quest = None
        self.selected_heroes = []
        self.description_box.configure(state="normal")
        self.description_box.delete("1.0", "end")
        self.description_box.insert("end", "Selecione uma missão para ver os detalhes.")
        self.description_box.configure(state="disabled")
        self.heroes_label.configure(text="Heróis Selecionados: Nenhum")
        self.result_label.configure(text="")
