# screens/gameplay/background_helper.py
import customtkinter as ctk
from PIL import Image, ImageTk


class BackgroundPanel(ctk.CTkFrame):
    """Frame com imagem de fundo personalizada (pergaminho com bordas)"""
    
    def __init__(self, parent, image_path="assets/parchment_bg.png", **kwargs):
        # Remove fg_color dos kwargs se existir
        kwargs.pop('fg_color', None)
        
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.image_path = image_path
        self.bg_label = None
        self.original_image = None
        
        # Carrega a imagem original
        try:
            self.original_image = Image.open(self.image_path)
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            self.configure(fg_color=("#F4E4C1", "#3A3428"))
            return
        
        # Cria o label de fundo
        self.bg_label = ctk.CTkLabel(self, text="")
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Bind para redimensionamento
        self.bind("<Configure>", self._on_resize)
    
    def _on_resize(self, event):
        """Callback quando o frame é redimensionado"""
        if not self.original_image or not self.bg_label:
            return
        
        # Aguarda um pouco para evitar múltiplas chamadas
        if hasattr(self, '_resize_job'):
            self.after_cancel(self._resize_job)
        self._resize_job = self.after(100, self._update_background_image)
    
    def _update_background_image(self):
        """Atualiza o tamanho da imagem mantendo as bordas visíveis"""
        if not self.original_image or not self.bg_label:
            return
        
        try:
            width = self.winfo_width()
            height = self.winfo_height()
            
            if width <= 1 or height <= 1:
                return
            
            # Calcula proporção mantendo aspect ratio
            img_width, img_height = self.original_image.size
            img_ratio = img_width / img_height
            frame_ratio = width / height
            
            # Redimensiona mantendo proporção e mostrando bordas completas
            if frame_ratio > img_ratio:
                # Frame é mais largo - ajusta pela altura
                new_height = height
                new_width = int(height * img_ratio)
            else:
                # Frame é mais alto - ajusta pela largura
                new_width = width
                new_height = int(width / img_ratio)
            
            # Redimensiona a imagem
            img_resized = self.original_image.resize(
                (new_width, new_height), 
                Image.Resampling.LANCZOS
            )
            
            # Converte para CTkImage
            photo = ctk.CTkImage(
                light_image=img_resized,
                dark_image=img_resized,
                size=(new_width, new_height)
            )
            
            self.bg_label.configure(image=photo)
            self.bg_label.image = photo  # Mantém referência
            
        except Exception as e:
            print(f"Erro ao redimensionar background: {e}")


class ParchmentPanel(ctk.CTkFrame):
    """Painel estilo pergaminho com imagem de fundo"""
    
    def __init__(self, parent, image_path="assets/parchment_bg.png", **kwargs):
        # Remove fg_color se existir
        kwargs.pop('fg_color', None)
        
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.image_path = image_path
        self.bg_canvas = None
        self.original_image = None
        
        # Carrega a imagem
        try:
            self.original_image = Image.open(self.image_path)
            self._setup_canvas()
        except Exception as e:
            print(f"Erro ao carregar pergaminho: {e}")
            # Fallback: cor sólida
            self.configure(
                fg_color=("#F4E4C1", "#3A3428"),
                corner_radius=10,
                border_width=3,
                border_color=("#8B7355", "#2A2420")
            )
    
    def _setup_canvas(self):
        """Configura canvas para o background"""
        from tkinter import Canvas
        
        # Canvas para desenhar a imagem
        self.bg_canvas = Canvas(
            self,
            highlightthickness=0,
            bg=self._apply_appearance_mode(("#F4E4C1", "#3A3428"))
        )
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Bind para redimensionamento
        self.bind("<Configure>", self._on_canvas_resize)
    
    def _on_canvas_resize(self, event):
        """Atualiza o canvas quando redimensiona"""
        if hasattr(self, '_canvas_job'):
            self.after_cancel(self._canvas_job)
        self._canvas_job = self.after(100, self._draw_background)
    
    def _draw_background(self):
        """Desenha a imagem no canvas mantendo bordas"""
        if not self.bg_canvas or not self.original_image:
            return
        
        try:
            width = self.winfo_width()
            height = self.winfo_height()
            
            if width <= 1 or height <= 1:
                return
            
            # Limpa canvas
            self.bg_canvas.delete("all")
            
            # Redimensiona mantendo proporção
            img = self.original_image.copy()
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Converte para PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Centraliza a imagem
            x = (width - img.width) // 2
            y = (height - img.height) // 2
            
            # Desenha no canvas
            self.bg_canvas.create_image(x, y, image=photo, anchor="nw")
            self.bg_canvas.image = photo  # Mantém referência
            
        except Exception as e:
            print(f"Erro ao desenhar background: {e}")


class StretchedParchmentPanel(ctk.CTkFrame):
    """Painel que estica a imagem de pergaminho (pode distorcer)"""
    
    def __init__(self, parent, image_path="assets/parchment_bg.png", **kwargs):
        kwargs.pop('fg_color', None)
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.image_path = image_path
        self.bg_label = None
        self.original_image = None
        
        try:
            self.original_image = Image.open(self.image_path)
            self.bg_label = ctk.CTkLabel(self, text="")
            self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.bind("<Configure>", self._on_resize)
        except Exception as e:
            print(f"Erro: {e}")
            self.configure(fg_color=("#F4E4C1", "#3A3428"))
    
    def _on_resize(self, event):
        if hasattr(self, '_job'):
            self.after_cancel(self._job)
        self._job = self.after(100, self._stretch_image)
    
    def _stretch_image(self):
        """Estica a imagem para preencher todo o espaço"""
        if not self.original_image or not self.bg_label:
            return
        
        try:
            width = self.winfo_width()
            height = self.winfo_height()
            
            if width <= 1 or height <= 1:
                return
            
            # Estica para preencher (pode distorcer)
            img_resized = self.original_image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )
            
            photo = ctk.CTkImage(
                light_image=img_resized,
                dark_image=img_resized,
                size=(width, height)
            )
            
            self.bg_label.configure(image=photo)
            self.bg_label.image = photo
            
        except Exception as e:
            print(f"Erro ao esticar imagem: {e}")


# Factories para facilitar o uso
def create_parchment_panel(parent, image_path="assets/parchment_bg.png", **kwargs):
    """Cria painel de pergaminho mantendo proporções"""
    return ParchmentPanel(parent, image_path=image_path, **kwargs)


def create_stretched_parchment(parent, image_path="assets/parchment_bg.png", **kwargs):
    """Cria painel de pergaminho esticado (preenche todo espaço)"""
    return StretchedParchmentPanel(parent, image_path=image_path, **kwargs)