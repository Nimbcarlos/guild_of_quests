import customtkinter
from PIL import Image

# Configurações iniciais do CustomTkinter
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuração da Janela ---
        self.geometry("800x600")
        self.title("Textbox Transparente sobre Imagem de Fundo")

        # --- 1. Carregar e Exibir a Imagem de Fundo ---
        # Substitua "assets/background_ls.png" pelo caminho correto da sua imagem
        # Usamos um tratamento de erro caso a imagem local não seja encontrada.
        
        background_image = None
        
        try:
            # Tenta carregar a imagem local
            img = Image.open("assets/background_ls.png")
            
            # Ajusta o tamanho da imagem para a janela
            bg_image = customtkinter.CTkImage(
                light_image=img,
                dark_image=img,
                size=(800, 600)
            )
            
            # Cria um CTkLabel para servir como fundo (preenche a janela inteira)
            background_label = customtkinter.CTkLabel(self, text="", image=bg_image)
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
            
        except FileNotFoundError:
            print("AVISO: Arquivo 'assets/background_ls.png' não encontrado. Usando cor de fundo padrão.")
            self.configure(fg_color="#343638") # Cor de fundo padrão se a imagem não for encontrada

        # --- 2. Criar o CTkTextbox Transparente ---
        
        # O CTkTextbox deve ser posicionado na parte inferior da tela, como uma caixa de diálogo
        self.transparent_textbox = customtkinter.CTkTextbox(
            self,
            width=760,
            height=150,
            
            # === CHAVES PARA A TRANSPARÊNCIA ===
            # fg_color="transparent", 
            border_width=0,          # Remove a borda padrão do Textbox
            
            # --- Configurações de Texto ---
            font=customtkinter.CTkFont(family="Inter", size=16),
            text_color="#000000",    # Cor clara para o texto, bom contraste com fundos escuros
            wrap="word",             # Quebra de linha por palavra
            
            # --- Configurações do Scrollbar ---
            scrollbar_button_color="#454545", # Cor discreta para o botão de rolagem
            scrollbar_button_hover_color="#6A6A6A"
        )
        
        # Posicionamento no centro inferior (simulando uma caixa de diálogo)
        self.transparent_textbox.place(
            relx=0.5,
            rely=0.9,
            anchor="center"
        )

        # --- 3. Inserir o Texto de Diálogo ---
        dialogue_text = (
            "Narrador: Onde os CustomTkinter Frames falham na transparência do canal alfa, "
            "devemos ser criativos! Ao configurar o 'fg_color' do widget como 'transparent', "
            "o fundo do widget desaparece, revelando o que está por baixo — neste caso, "
            "a imagem de fundo do nosso jogo ('background_ls.png').\n\n"
            "Personagem: Ah, então a ilusão de 'transparência real' é criada usando uma "
            "imagem de fundo na janela principal e definindo a cor de primeiro plano do "
            "nosso Textbox como transparente. Genial!"
        )
        
        # Desativa o estado de escrita para parecer um rótulo de diálogo (read-only)
        self.transparent_textbox.insert("0.0", dialogue_text)
        self.transparent_textbox.configure(state="disabled") 

if __name__ == "__main__":
    app = App()
    app.mainloop()
