"""
ventana_visualizar.py — Lista de pacientes con detalle al doble clic.
"""
import tkinter as tk
from tkinter import ttk

from core.constantes import COLOR_CLASIFICACION
from core.db import obtener_pacientes, obtener_paciente_por_id
from ui.ui_utils import agregar_firma, aplicar_icono, get_tema


def _abrir_detalle(vis: tk.Toplevel, id_paciente: int) -> None:
    row = obtener_paciente_por_id(id_paciente)
    if not row:
        return

    # Nuevo esquema: nombre, edad, sexo, peso, talla, imc, exceso_grasa, nivel_musculo, signos, imc_label, clasificacion, justificacion
    (nombre, edad, sexo, peso, talla, imc, exceso, musculo, signos,
     imc_label, clasificacion, justificacion) = row

    color    = COLOR_CLASIFICACION.get(clasificacion, "#555")
    sexo_txt = "Masculino" if sexo == "M" else "Femenino"
    t        = get_tema()

    det = tk.Toplevel(vis)
    det.title(f"Detalle — {nombre}")
    det.geometry("580x650") 
    det.resizable(True, True)
    det.configure(bg=t["bg"])
    det.grab_set()
    aplicar_icono(det)

    det.rowconfigure(1, weight=1)
    det.columnconfigure(0, weight=1)

    # 1. Encabezado
    header = tk.Frame(det, bg=color, pady=12)
    header.grid(row=0, column=0, sticky="ew")
    tk.Label(header, text=nombre, font=("Segoe UI", 14, "bold"),
             bg=color, fg="white").pack()
    tk.Label(header, text=clasificacion, font=("Segoe UI", 11),
             bg=color, fg="white").pack()

    # 2. Área Central con Scroll
    content_area = tk.Frame(det, bg=t["bg"])
    content_area.grid(row=1, column=0, sticky="nsew")

    canvas = tk.Canvas(content_area, bg=t["bg"], highlightthickness=0)
    vsb = tk.Scrollbar(content_area, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    body = tk.Frame(canvas, padx=28, pady=16, bg=t["bg"])
    fid = canvas.create_window((0, 0), window=body, anchor="nw")
    
    body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(fid, width=e.width))

    datos = [
        ("ID",               str(id_paciente)),
        ("Edad",             f"{edad} años"),
        ("Sexo",             sexo_txt),
        ("Peso",             f"{peso} kg"),
        ("Talla",            f"{talla} m"),
        ("IMC",              f"{imc}  —  {imc_label}"),
        ("Exceso de grasa",  exceso),
        ("Masa muscular",    musculo),
        ("Signos/Síntomas",  signos or "Sin signos"),
    ]

    for i, (lbl, val) in enumerate(datos):
        tk.Label(body, text=lbl + ":", font=("Segoe UI", 9, "bold"),
                 anchor="w", width=18, bg=t["bg"], fg=t["fg"]).grid(
            row=i, column=0, sticky="w", pady=3)
        tk.Label(body, text=val, anchor="w", wraplength=300,
                 justify="left", bg=t["bg"], fg=t["fg"]).grid(
            row=i, column=1, sticky="w", pady=3, padx=8)

    tk.Frame(body, height=1, bg=t["border"]).grid(
        row=len(datos), column=0, columnspan=2, sticky="ew", pady=(10, 6))

    tk.Label(body, text="Justificación:", font=("Segoe UI", 9, "bold"),
             anchor="w", bg=t["bg"], fg=t["fg"]).grid(
        row=len(datos)+1, column=0, columnspan=2, sticky="w")
    tk.Label(body, text=justificacion or "—", wraplength=460,
             justify="left", fg=t["fg_sub"], font=("Segoe UI", 9),
             bg=t["bg"]).grid(
        row=len(datos)+2, column=0, columnspan=2, sticky="w", pady=(4, 0))

    # 3. Botón Cerrar
    footer = tk.Frame(det, bg=t["bg"], pady=12, highlightbackground=t["border"], highlightthickness=1)
    footer.grid(row=2, column=0, sticky="ew")
    tk.Button(footer, text="Cerrar", command=det.destroy,
              width=14, font=("Segoe UI", 10),
              bg="#3B82F6", fg="white", relief="flat",
              activebackground="#2563EB", cursor="hand2").pack()


def abrir_visualizar(ventana_root: tk.Tk, menu: tk.Toplevel) -> None:
    menu.withdraw()
    t = get_tema()

    vis = tk.Toplevel(ventana_root)
    vis.title("Lista de Pacientes")
    vis.geometry("1100x520")
    vis.configure(bg=t["bg"])
    aplicar_icono(vis)

    hf = tk.Frame(vis, bg=t["bg_header"], pady=10)
    hf.pack(fill="x")
    tk.Label(hf, text="📋  Lista de Pacientes",
             font=("Segoe UI", 13, "bold"),
             bg=t["bg_header"], fg="white").pack(side="left", padx=20)
    tk.Label(hf, text="© rogsaltt-pix",
             font=("Segoe UI", 8, "italic"),
             bg=t["bg_header"], fg="#94A3B8").pack(side="right", padx=16)

    style = ttk.Style()
    style.theme_use("clam")
    if t["bg"] == "#0F172A":
        style.configure("Treeview", background="#1E293B",
                        fieldbackground="#1E293B", foreground="#F1F5F9",
                        rowheight=26, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#0A1628",
                        foreground="white", font=("Segoe UI", 9, "bold"))
    else:
        style.configure("Treeview", background="white",
                        fieldbackground="white", foreground="#1E293B",
                        rowheight=26, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#1A2B4A",
                        foreground="white", font=("Segoe UI", 9, "bold"))

    # Columnas simplificadas para el nuevo esquema
    columnas = ("ID", "Nombre", "Edad", "Sexo", "Peso", "Talla", "IMC",
                "Exceso Grasa", "Masa Muscular", "Signos", "Clasificación")
    anchos = [40, 150, 50, 70, 60, 60, 60, 100, 110, 180, 150]

    frame_tabla = tk.Frame(vis, bg=t["bg"])
    frame_tabla.pack(fill="both", expand=True, padx=10, pady=8)

    tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
    for col, w in zip(columnas, anchos):
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center", width=w)

    if t["bg"] == "#0F172A":
        tabla.tag_configure("Sin obesidad",        background="#14532D", foreground="#F1F5F9")
        tabla.tag_configure("Obesidad preclínica", background="#78350F", foreground="#F1F5F9")
        tabla.tag_configure("Obesidad clínica",    background="#7F1D1D", foreground="#F1F5F9")
    else:
        tabla.tag_configure("Sin obesidad",        background="#DCFCE7")
        tabla.tag_configure("Obesidad preclínica", background="#FEF3C7")
        tabla.tag_configure("Obesidad clínica",    background="#FEE2E2")

    sx = ttk.Scrollbar(frame_tabla, orient="horizontal", command=tabla.xview)
    sy = ttk.Scrollbar(frame_tabla, orient="vertical",   command=tabla.yview)
    tabla.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
    sy.pack(side="right", fill="y")
    tabla.pack(fill="both", expand=True)
    sx.pack(fill="x")

    def cargar():
        for row in tabla.get_children():
            tabla.delete(row)
        for r in obtener_pacientes():
            # r: id, nombre, edad, sexo, peso, talla, imc, exceso_grasa, nivel_musculo, signos_sintomas, clasificacion_final
            r = list(r)
            tag = r[10] if r[10] in COLOR_CLASIFICACION else ""
            tabla.insert("", tk.END, values=r, tags=(tag,))

    tabla.bind("<Double-Button-1>",
               lambda e: _abrir_detalle(vis, tabla.item(tabla.selection()[0])["values"][0])
               if tabla.selection() else None)

    def volver():
        vis.destroy()
        menu.deiconify()

    bf = tk.Frame(vis, bg=t["bg"], pady=6)
    bf.pack()
    for texto, cmd, color in [
        ("🔄  Actualizar", cargar, "#3B82F6"),
        ("↩  Volver al menú", volver, "#64748B"),
    ]:
        tk.Button(bf, text=texto, command=cmd,
                  bg=color, fg="white", font=("Segoe UI", 9),
                  relief="flat", cursor="hand2", padx=12, pady=6,
                  activebackground="#1E293B", activeforeground="white"
                  ).pack(side="left", padx=6)

    tk.Label(vis, text="Doble clic en un paciente para ver su detalle",
             font=("Segoe UI", 8), fg=t["fg_sub"], bg=t["bg"]).pack()

    vis.protocol("WM_DELETE_WINDOW", volver)
    cargar()
