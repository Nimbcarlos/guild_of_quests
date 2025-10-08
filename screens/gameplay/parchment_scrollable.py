# screens/gameplay/parchment_scrollable.py
import customtkinter as ctk
from PIL import Image, ImageTk
from tkinter import Canvas


class ParchmentScrollableFrame(ctk.CTkScrollableFrame):
    """ScrollableFrame com imagem de pergaminho de fundo"""
    
    def __init__(self, parent, image_path="assets/parchment_bg.png", **kwargs):
        # Remove fg_color se existir
        kwargs.pop('fg_color', None)
        
        # Inicializa o ScrollableFrame
        super().__init__(
            parent,
            fg_color="transparent",
            scrollbar_button_color="#8B7355",
            scrollbar_button_hover_color="#6B5535",
            **kwargs
        )
        
        self.image_path = image_path
        self.original_image = None
        self.bg_canvas = None
        self.photo_image = None
        
        # Carrega a imagem
        try:
            self.original_image = Image.open(self.image_path)
            self._setup_background()
        except Exception as e:
            print(f"Erro ao carregar pergaminho: {e}")
    
    def _setup_background(self):
        """Configura o background de pergaminho no canvas interno"""
        # Acessa o canvas interno do ScrollableFrame
        try:
            # O canvas interno é armazenado em _parent_canvas
            canvas = self._parent_canvas
            
            # Armazena referência
            self.bg_canvas = canvas
            
            # Configura cor de fundo base (caso a imagem não carregue)
            canvas.configure(bg='#F4E4C1', highlightthickness=0)
            
            # Bind para redimensionamento
            canvas.bind("<Configure>", self._on_canvas_resize)
            
            # Frame interno também transparente
            self._parent_frame.configure(fg_color="transparent")
            
        except Exception as e:
            print(f"Erro ao configurar background: {e}")
    
    def _on_canvas_resize(self, event):
        """Callback quando o canvas é redimensionado"""
        if hasattr(self, '_resize_job'):
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(100, self._draw_parchment)
    
    def _draw_parchment(self):
        """Desenha a imagem de pergaminho no canvas"""
        if not self.bg_canvas or not self.original_image:
            return
        
        try:
            # Pega dimensões do canvas
            width = self.bg_canvas.winfo_width()
            height = self.bg_canvas.winfo_height()
            
            if width <= 1 or height <= 1:
                return
            
            # Remove imagem anterior se existir
            self.bg_canvas.delete("parchment_bg")
            
            # Redimensiona a imagem para o tamanho do canvas
            img_resized = self.original_image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )
            
            # Converte para PhotoImage
            self.photo_image = ImageTk.PhotoImage(img_resized)
            
            # Desenha no canvas (tag para poder deletar depois)
            self.bg_canvas.create_image(
                0, 0,
                image=self.photo_image,
                anchor="nw",
                tags="parchment_bg"
            )
            
            # Move o background para trás de tudo
            self.bg_canvas.tag_lower("parchment_bg")
            
        except Exception as e:
            print(f"Erro ao desenhar pergaminho: {e}")


# Helper function para criar facilmente
def create_parchment_scrollable(parent, image_path="assets/parchment_bg.png", **kwargs):
    """Cria um ScrollableFrame com fundo de pergaminho"""
    return ParchmentScrollableFrame(parent, image_path=image_path, **kwargs)