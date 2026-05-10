"""
ui_utils.py — Utilidades UI: firma, icono y modo oscuro.
"""
import tkinter as tk

# ── Tema global ───────────────────────────────────────────────────────────────
_modo_oscuro = False

TEMAS = {
    "claro": {
        "bg":         "#F0F4F8",
        "bg_panel":   "#FFFFFF",
        "bg_header":  "#1A2B4A",
        "fg":         "#1E293B",
        "fg_sub":     "#64748B",
        "fg_header":  "#FFFFFF",
        "entry_bg":   "#FFFFFF",
        "entry_fg":   "#1E293B",
        "btn_bg":     "#E2E8F0",
        "btn_fg":     "#1E293B",
        "border":     "#CBD5E1",
        "sel_bg":     "#BFDBFE",
        "listbox_sel":"#DBEAFE",
    },
    "oscuro": {
        "bg":         "#0F172A",
        "bg_panel":   "#1E293B",
        "bg_header":  "#0A1628",
        "fg":         "#F1F5F9",
        "fg_sub":     "#94A3B8",
        "fg_header":  "#F1F5F9",
        "entry_bg":   "#334155",
        "entry_fg":   "#F1F5F9",
        "btn_bg":     "#334155",
        "btn_fg":     "#F1F5F9",
        "border":     "#475569",
        "sel_bg":     "#1D4ED8",
        "listbox_sel":"#1E3A5F",
    },
}

_ventanas_registradas: list = []   # (ventana, callback_aplicar)


def get_tema() -> dict:
    return TEMAS["oscuro"] if _modo_oscuro else TEMAS["claro"]


def es_oscuro() -> bool:
    return _modo_oscuro


def registrar_ventana(ventana: tk.BaseWidget, callback) -> None:
    """Registra una ventana para recibir cambios de tema."""
    _ventanas_registradas.append((ventana, callback))


def toggle_modo_oscuro() -> None:
    global _modo_oscuro
    _modo_oscuro = not _modo_oscuro
    # Notificar a todas las ventanas abiertas
    vivas = []
    for v, cb in _ventanas_registradas:
        try:
            v.winfo_exists()
            cb()
            vivas.append((v, cb))
        except Exception:
            pass
    _ventanas_registradas.clear()
    _ventanas_registradas.extend(vivas)


# ── Firma e icono ─────────────────────────────────────────────────────────────

def agregar_firma(parent: tk.BaseWidget) -> None:
    t = get_tema()
    footer = tk.Frame(parent, bg=t["bg_header"])
    footer.pack(side="bottom", fill="x")
    tk.Label(
        footer,
        text="© rogsaltt-pix",
        font=("Segoe UI", 8, "italic"),
        fg="#94A3B8",
        bg=t["bg_header"],
    ).pack(pady=4)


def aplicar_icono(ventana: tk.BaseWidget) -> None:
    try:
        ventana.iconbitmap("assets/icon.ico")
    except Exception:
        pass


# ── Helper para aplicar tema a un widget y sus hijos ─────────────────────────

def _aplicar_bg(widget, bg, fg, entry_bg, entry_fg, btn_bg, btn_fg, border):
    cls = widget.winfo_class()
    try:
        if cls in ("Frame", "Toplevel", "Canvas"):
            widget.configure(bg=bg)
        elif cls == "Label":
            # No tocar labels dentro de frames de color de clasificación
            widget.configure(bg=bg, fg=fg)
        elif cls == "Entry":
            widget.configure(bg=entry_bg, fg=entry_fg,
                             insertbackground=fg,
                             highlightbackground=border)
        elif cls == "Button":
            widget.configure(bg=btn_bg, fg=btn_fg,
                             activebackground=border,
                             activeforeground=fg)
        elif cls == "Listbox":
            widget.configure(bg=entry_bg, fg=entry_fg,
                             selectbackground=border)
        elif cls == "LabelFrame":
            widget.configure(bg=bg, fg=fg)
        elif cls == "Radiobutton":
            widget.configure(bg=bg, fg=fg, selectcolor=entry_bg,
                             activebackground=bg, activeforeground=fg)
        elif cls == "Checkbutton":
            widget.configure(bg=bg, fg=fg, selectcolor=entry_bg)
    except Exception:
        pass

    for child in widget.winfo_children():
        _aplicar_bg(child, bg, fg, entry_bg, entry_fg, btn_bg, btn_fg, border)


def aplicar_tema_ventana(ventana: tk.BaseWidget) -> None:
    """Aplica el tema actual a toda la ventana."""
    t = get_tema()
    _aplicar_bg(
        ventana,
        bg=t["bg"], fg=t["fg"],
        entry_bg=t["entry_bg"], entry_fg=t["entry_fg"],
        btn_bg=t["btn_bg"], btn_fg=t["btn_fg"],
        border=t["border"],
    )
