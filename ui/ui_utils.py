"""
----------------Autenticacion
"""
import tkinter as tk

def agregar_firma(parent):
    footer = tk.Frame(parent)
    footer.pack(side="bottom", fill="x")

    tk.Label(
        footer,
        text="Hecho por rogsaltt-pix",
        font=("Arial", 8),
        fg="#888"
    ).pack(pady=4)

"------------- Todas las ventanas tienen icono"
def aplicar_icono(ventana):
    ventana.iconbitmap("assets/icon.ico")