"""
main.py — Punto de entrada. Solo inicialización y menú principal.
"""
import tkinter as tk
from ui.ui_utils import agregar_firma, aplicar_icono

try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

from core.db import inicializar_db
from ui.ventana_registro   import abrir_registro
from ui.ventana_visualizar import abrir_visualizar
from ui.ventana_eliminar   import abrir_eliminar_paciente


def abrir_menu(ventana_root: tk.Tk) -> None:
    menu = tk.Toplevel(ventana_root)
    menu.title("Sistema de Clasificación de Obesidad")
    menu.geometry("420x280")
    menu.resizable(False, False)
    agregar_firma(menu)
    aplicar_icono(menu)

    tk.Label(menu, text="Sistema de Clasificación\nde Obesidad",
             font=("Arial", 13, "bold"), justify="center").pack(pady=16)

    tk.Button(
        menu, text="➕  Registrar paciente",
        command=lambda: abrir_registro(ventana_root, menu),
        width=24
    ).pack(pady=5)

    tk.Button(
        menu, text="📋  Ver pacientes",
        command=lambda: abrir_visualizar(ventana_root, menu),
        width=24
    ).pack(pady=5)

    tk.Button(
        menu, text="🗑  Eliminar paciente",
        command=lambda: [menu.withdraw(),
                         abrir_eliminar_paciente(ventana_root, menu)],
        bg="#e74c3c", fg="white", width=24
    ).pack(pady=5)

    menu.protocol("WM_DELETE_WINDOW", ventana_root.destroy)


if __name__ == "__main__":
    inicializar_db()
    root = tk.Tk()
    root.iconbitmap("assets/icon.ico")
    root.withdraw()
    abrir_menu(root)
    root.mainloop()