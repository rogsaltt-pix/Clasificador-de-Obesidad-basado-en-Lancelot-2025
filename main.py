"""
main.py — Punto de entrada. Solo inicialización y menú principal.
"""
import tkinter as tk
from ui.ui_utils import (agregar_firma, aplicar_icono, toggle_modo_oscuro,
                          aplicar_tema_ventana, registrar_ventana, get_tema, es_oscuro, resource_path)
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
    menu.geometry("360x600")
    menu.resizable(False, False)
    aplicar_icono(menu)

    def construir():
        # Limpiar ventana
        for w in menu.winfo_children():
            w.destroy()
        
        t = get_tema()
        menu.configure(bg=t["bg_header"])

        # ── Encabezado ────────────────────────────────────────────────────────
        hf = tk.Frame(menu, bg=t["bg_header"])
        hf.pack(fill="x", pady=(0, 0))
        
        tk.Label(hf, text="🍎", font=("Segoe UI", 32),
                 bg=t["bg_header"], fg=t["fg_header"]).pack(pady=(20, 4))
        
        tk.Label(hf, text="Clasificación de Obesidad",
                 font=("Segoe UI", 14, "bold"),
                 bg=t["bg_header"], fg=t["fg_header"]).pack()
        
        tk.Label(hf, text="Criterio Lancet 2025",
                 font=("Segoe UI", 8),
                 bg=t["bg_header"], fg="#94A3B8").pack(pady=(2, 0))

        # ── Leyenda ───────────────────────────────────────────────────────────
        lf = tk.Frame(hf, bg=t["bg_header"])
        lf.pack(pady=10)
        for texto, color, bg in [
            ("Sin obesidad",        "#16A34A", "#DCFCE7"),
            ("Preclínica",          "#D97706", "#FEF3C7"),
            ("Clínica",             "#DC2626", "#FEE2E2"),
        ]:
            tk.Label(lf, text=f" {texto} ", font=("Segoe UI", 7, "bold"),
                     fg=color, bg=bg).pack(side="left", padx=3)

        # ── Botones ───────────────────────────────────────────────────────────
        body = tk.Frame(menu, bg=t["bg"], padx=30, pady=20)
        body.pack(fill="both", expand=True)

        estilo_btn = dict(font=("Segoe UI", 10), relief="flat",
                          cursor="hand2", pady=8, width=26)

        def btn_primario(texto, cmd):
            b = tk.Button(body, text=texto, command=cmd,
                          bg="#3B82F6", fg="white",
                          activebackground="#2563EB", activeforeground="white",
                          **estilo_btn)
            b.pack(pady=6, fill="x")

        def btn_peligro(texto, cmd):
            b = tk.Button(body, text=texto, command=cmd,
                          bg="#EF4444", fg="white",
                          activebackground="#DC2626", activeforeground="white",
                          **estilo_btn)
            b.pack(pady=6, fill="x")

        btn_primario("➕   Registrar paciente",
                     lambda: abrir_registro(ventana_root, menu))
        btn_primario("📋   Ver pacientes",
                     lambda: abrir_visualizar(ventana_root, menu))
        btn_peligro("🗑   Eliminar paciente",
                    lambda: [menu.withdraw(),
                             abrir_eliminar_paciente(ventana_root, menu)])

        # ── Toggle modo oscuro ────────────────────────────────────────────────
        icono_modo = "☀️  Modo claro" if es_oscuro() else "🌙  Modo oscuro"
        tk.Button(
            body, text=icono_modo,
            command=toggle_modo_oscuro,
            bg=t["btn_bg"], fg=t["fg"],
            font=("Segoe UI", 9), relief="flat",
            cursor="hand2", pady=6, width=26,
            activebackground=t["border"],
        ).pack(pady=(4, 0), fill="x")

        # ── Firma ─────────────────────────────────────────────────────────────
        pie = tk.Frame(menu, bg=t["bg_header"])
        pie.pack(fill="x", side="bottom")
        tk.Label(pie, text="© rogsaltt-pix",
                 font=("Segoe UI", 8, "italic"),
                 fg="#94A3B8", bg=t["bg_header"]).pack(pady=6)

    construir()
    registrar_ventana(menu, construir)
    menu.protocol("WM_DELETE_WINDOW", ventana_root.destroy)

if __name__ == "__main__":
    inicializar_db()
    root = tk.Tk()
    try:
        icono_path = resource_path("assets/icon.ico")
        root.iconbitmap(icono_path)
    except Exception:
        pass
    root.withdraw()
    abrir_menu(root)
    root.mainloop()
