# screens/gameplay/opacity_helper.py
"""
Helper para definir opacidade em widgets CustomTkinter (Windows only)
Baseado em: https://stackoverflow.com/questions/...
"""

import platform


def set_opacity(widget, value: float):
    """
    Define a opacidade de um widget (funciona apenas no Windows).
    
    Args:
        widget: Widget do CustomTkinter/Tkinter
        value (float): Opacidade de 0.0 (transparente) a 1.0 (opaco)
    
    Returns:
        bool: True se funcionou, False se não suportado
    """
    # Só funciona no Windows
    if platform.system() != 'Windows':
        print("⚠️ Opacidade não suportada neste sistema operacional")
        return False
    
    try:
        from ctypes import windll
        
        # Pega o ID da janela do widget
        hwnd = widget.winfo_id()
        
        # Converte opacidade de 0.0-1.0 para 0-255
        alpha = int(255 * value)
        
        # Pega o estilo atual da janela
        wnd_exstyle = windll.user32.GetWindowLongW(hwnd, -20)  # GWL_EXSTYLE = -20
        
        # Adiciona WS_EX_LAYERED (0x00080000) para permitir transparência
        new_exstyle = wnd_exstyle | 0x00080000
        windll.user32.SetWindowLongW(hwnd, -20, new_exstyle)
        
        # Define a opacidade usando SetLayeredWindowAttributes
        # Parâmetros: hwnd, crKey, bAlpha, dwFlags
        # dwFlags: LWA_ALPHA = 2
        windll.user32.SetLayeredWindowAttributes(hwnd, 0, alpha, 2)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao definir opacidade: {e}")
        return False


def make_transparent(widget, opacity=0.0):
    """
    Torna um widget completamente transparente ou semi-transparente.
    
    Args:
        widget: Widget do CustomTkinter/Tkinter
        opacity (float): 0.0 = invisível, 1.0 = opaco
    """
    return set_opacity(widget, opacity)


def make_semi_transparent(widget):
    """Torna um widget semi-transparente (50%)"""
    return set_opacity(widget, 0.5)


def make_opaque(widget):
    """Torna um widget completamente opaco"""
    return set_opacity(widget, 1.0)


# Exemplo de uso com CustomTkinter
if __name__ == "__main__":
    import customtkinter as ctk
    
    app = ctk.CTk()
    app.title("Teste de Opacidade")
    app.geometry("400x300")
    
    # Frame de fundo
    bg_frame = ctk.CTkFrame(app, fg_color="blue")
    bg_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Botão normal
    btn1 = ctk.CTkButton(bg_frame, text="Botão Normal")
    btn1.pack(pady=10)
    
    # Botão semi-transparente
    btn2 = ctk.CTkButton(bg_frame, text="Botão 50% Transparente")
    btn2.pack(pady=10)
    
    # Frame semi-transparente
    frame = ctk.CTkFrame(bg_frame, fg_color="green", width=200, height=100)
    frame.pack(pady=10)
    
    # Aplica opacidade após um pequeno delay (garante que widget está visível)
    app.after(100, lambda: make_semi_transparent(btn2))
    app.after(100, lambda: set_opacity(frame, 0.3))
    
    app.mainloop()