"""
ventana_visualizar.py — Lista de pacientes con detalle al doble clic.
"""
import tkinter as tk
from tkinter import ttk

from core.constantes import COLOR_CLASIFICACION
from core.db import obtener_pacientes, obtener_paciente_por_id
from ui.ui_utils import agregar_firma, aplicar_icono


def _abrir_detalle(vis: tk.Toplevel, id_paciente: int) -> None:
    row = obtener_paciente_por_id(id_paciente)
    if not row:
        return

    (nombre, edad, sexo, peso, talla, imc, grasa, musculo, signos,
     imc_label, exceso, musc_bajo, danio, clasificacion, justificacion) = row

    color    = COLOR_CLASIFICACION.get(clasificacion, "#555")
    sexo_txt = "Masculino" if sexo == "M" else "Femenino"

    det = tk.Toplevel(vis)
    det.title(f"Detalle — {nombre}")
    det.geometry("520x560")
    det.resizable(False, False)
    det.grab_set()

    # Encabezado
    header = tk.Frame(det, bg=color, pady=12)
    header.pack(fill="x")
    tk.Label(header, text=nombre, font=("Arial", 14, "bold"),
             bg=color, fg="white").pack()
    tk.Label(header, text=clasificacion, font=("Arial", 11),
             bg=color, fg="white").pack()

    body = tk.Frame(det, padx=24, pady=16)
    body.pack(fill="both", expand=True)

    datos = [
        ("ID",               str(id_paciente)),
        ("Edad",             f"{edad} años"),
        ("Sexo",             sexo_txt),
        ("Peso",             f"{peso} kg"),
        ("Talla",            f"{talla} m"),
        ("IMC",              f"{imc}  —  {imc_label}"),
        ("% Grasa corporal", f"{grasa}%  ({'↑ Exceso' if exceso else '✓ Normal'})"),
        ("% Masa muscular",  f"{musculo}%  ({'↓ Bajo' if musc_bajo else '✓ Normal'})"),
        ("Daño orgánico",    "Sí" if danio else "No"),
        ("Signos/Síntomas",  signos or "Sin signos"),
    ]

    for i, (lbl, val) in enumerate(datos):
        tk.Label(body, text=lbl + ":", font=("Arial", 9, "bold"),
                 anchor="w", width=18).grid(row=i, column=0, sticky="w", pady=3)
        tk.Label(body, text=val, anchor="w", wraplength=280,
                 justify="left").grid(row=i, column=1, sticky="w", pady=3, padx=8)

    tk.Frame(body, height=1, bg="#ddd").grid(
        row=len(datos), column=0, columnspan=2, sticky="ew", pady=(10, 6)
    )
    tk.Label(body, text="Justificación:", font=("Arial", 9, "bold"),
             anchor="w").grid(row=len(datos)+1, column=0, columnspan=2, sticky="w")
    tk.Label(body, text=justificacion or "—", wraplength=440,
             justify="left", fg="#333", font=("Arial", 9)).grid(
        row=len(datos)+2, column=0, columnspan=2, sticky="w", pady=(4, 0)
    )

    tk.Button(det, text="Cerrar", command=det.destroy,
              width=14, font=("Arial", 10)).pack(pady=14)


def abrir_visualizar(ventana_root: tk.Tk, menu: tk.Toplevel) -> None:
    menu.withdraw()

    vis = tk.Toplevel(ventana_root)
    vis.title("Lista de Pacientes")
    vis.geometry("1200x500")
    agregar_firma(vis)
    aplicar_icono(vis)

    columnas = (
        "ID", "Nombre", "Edad", "Sexo", "Peso", "Talla", "IMC",
        "% Grasa", "% Músculo", "Signos", "IMC Clasif.",
        "Exceso grasa", "Músculo bajo", "Daño org.", "Clasificación"
    )
    anchos = [40, 130, 50, 50, 60, 60, 60, 70, 80, 150, 110, 90, 90, 80, 130]

    tabla = ttk.Treeview(vis, columns=columnas, show="headings")
    for col, w in zip(columnas, anchos):
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center", width=w)

    tabla.tag_configure("Sin obesidad",        background="#d5f5e3")
    tabla.tag_configure("Obesidad preclínica", background="#fdebd0")
    tabla.tag_configure("Obesidad clínica",    background="#fadbd8")

    scroll_x = ttk.Scrollbar(vis, orient="horizontal", command=tabla.xview)
    scroll_y = ttk.Scrollbar(vis, orient="vertical",   command=tabla.yview)
    tabla.configure(xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

    tabla.pack(fill="both", expand=True)
    scroll_x.pack(fill="x")

    def cargar():
        for row in tabla.get_children():
            tabla.delete(row)
        for r in obtener_pacientes():
            r = list(r)
            r[11] = "Sí" if r[11] else "No"
            r[12] = "Sí" if r[12] else "No"
            r[13] = "Sí" if r[13] else "No"
            tag = r[14] if r[14] in COLOR_CLASIFICACION else ""
            tabla.insert("", tk.END, values=r, tags=(tag,))

    def on_doble_clic(event):
        sel = tabla.selection()
        if sel:
            id_paciente = tabla.item(sel[0])["values"][0]
            _abrir_detalle(vis, id_paciente)

    tabla.bind("<Double-Button-1>", on_doble_clic)

    def volver():
        vis.destroy()
        menu.deiconify()

    btn_frame = tk.Frame(vis)
    btn_frame.pack(pady=6)
    tk.Button(btn_frame, text="Actualizar",    command=cargar, width=14).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Volver al menú", command=volver, width=14).pack(side="left", padx=6)

    tk.Label(vis, text="Doble clic en un paciente para ver su detalle",
             font=("Arial", 8), fg="#888").pack()

    vis.protocol("WM_DELETE_WINDOW", volver)
    cargar()
