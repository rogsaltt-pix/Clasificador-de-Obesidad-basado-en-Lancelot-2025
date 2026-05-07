"""
ventana_registro.py — Formulario de registro de nuevos pacientes.
"""
import tkinter as tk
from tkinter import messagebox

from core.constantes import COLOR_CLASIFICACION, TODOS_LOS_SIGNOS
from core.clasificacion import calcular_imc, clasificar_obesidad
from core.db import guardar_paciente
from ui.ui_utils import agregar_firma, aplicar_icono

# ── Ventana de confirmación ───────────────────────────────────────────────────

def mostrar_confirmacion(parent: tk.Toplevel, nombre: str, resultado: dict) -> None:
    color = COLOR_CLASIFICACION.get(resultado["clasificacion"], "#333")

    win = tk.Toplevel(parent)
    win.title("Paciente guardado")
    win.geometry("420x360")
    win.resizable(False, False)
    win.grab_set()

    header = tk.Frame(win, bg="#2ecc71", pady=14)
    header.pack(fill="x")
    tk.Label(header, text="✔  Paciente guardado correctamente",
             font=("Arial", 12, "bold"), bg="#2ecc71", fg="white").pack()

    body = tk.Frame(win, padx=24, pady=16)
    body.pack(fill="both", expand=True)

    filas = [
        ("Nombre:",          nombre),
        ("IMC:",             resultado["imc_label"]),
        ("Exceso de grasa:", "Sí" if resultado["exceso_grasa"] else "No"),
        ("Daño orgánico:",   "Sí" if resultado["danio_organico"] else "No"),
    ]
    for i, (lbl, val) in enumerate(filas):
        tk.Label(body, text=lbl, font=("Arial", 10, "bold"), anchor="w").grid(
            row=i, column=0, sticky="w", pady=3)
        tk.Label(body, text=val, anchor="w").grid(
            row=i, column=1, sticky="w", pady=3, padx=8)

    cf = tk.Frame(body, bg=color, pady=8, padx=12)
    cf.grid(row=len(filas), column=0, columnspan=2, sticky="ew", pady=(12, 4))
    tk.Label(cf, text="Clasificación:",
             font=("Arial", 10), bg=color, fg="white").pack(side="left")
    tk.Label(cf, text=resultado["clasificacion"],
             font=("Arial", 11, "bold"), bg=color, fg="white").pack(side="left", padx=8)

    tk.Button(win, text="Aceptar", command=win.destroy,
              width=16, font=("Arial", 10, "bold")).pack(pady=20)

    win.transient(parent)
    parent.wait_window(win)


# ── Widget de Signos / Síntomas ───────────────────────────────────────────────

def crear_widget_signos(frame: tk.Frame, fila: int) -> tuple:
    """
    Construye el panel de búsqueda y selección de signos/síntomas.
    Retorna (get_signos, limpiar_signos) — funciones para leer y limpiar.
    """
    signos_seleccionados = []

    panel = tk.LabelFrame(frame, text="Signos / Síntomas",
                          padx=8, pady=8, font=("Arial", 10, "bold"))
    panel.grid(row=fila, column=0, columnspan=2, sticky="ew", pady=(10, 4))

    # ── Columna izquierda ─────────────────────────────────────────────────────
    col_izq = tk.Frame(panel)
    col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

    tk.Label(col_izq, text="Buscar:", font=("Arial", 9, "bold")).pack(anchor="w")
    buscar_var = tk.StringVar()
    tk.Entry(col_izq, textvariable=buscar_var, width=28,
             font=("Arial", 10)).pack(fill="x", pady=(2, 4))

    filtro_var = tk.StringVar(value="Todos")
    ff = tk.Frame(col_izq)
    ff.pack(anchor="w", pady=(0, 4))
    for op in ("Todos", "Signos", "Síntomas"):
        tk.Radiobutton(ff, text=op, variable=filtro_var,
                       value=op, font=("Arial", 8)).pack(side="left")

    lf1 = tk.Frame(col_izq)
    lf1.pack(fill="both", expand=True)
    sb1 = tk.Scrollbar(lf1, orient="vertical")
    listbox = tk.Listbox(lf1, height=9, width=30, yscrollcommand=sb1.set,
                         selectmode="single", exportselection=False,
                         font=("Arial", 9), activestyle="dotbox", cursor="hand2")
    sb1.config(command=listbox.yview)
    listbox.pack(side="left", fill="both", expand=True)
    sb1.pack(side="left", fill="y")
    tk.Label(col_izq, text="Doble clic para agregar",
             font=("Arial", 8), fg="#888").pack(anchor="w", pady=(3, 0))

    # ── Columna central ───────────────────────────────────────────────────────
    col_mid = tk.Frame(panel)
    col_mid.grid(row=0, column=1, padx=6, sticky="ns")
    tk.Label(col_mid, text="").pack(pady=20)

    # ── Columna derecha ───────────────────────────────────────────────────────
    col_der = tk.Frame(panel)
    col_der.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

    tk.Label(col_der, text="Seleccionados:", font=("Arial", 9, "bold")).pack(anchor="w")
    lf2 = tk.Frame(col_der)
    lf2.pack(fill="both", expand=True, pady=(4, 0))
    sb2 = tk.Scrollbar(lf2, orient="vertical")
    listbox_sel = tk.Listbox(lf2, height=9, width=30, yscrollcommand=sb2.set,
                              selectmode="single", exportselection=False,
                              font=("Arial", 9), bg="#f0f7f0", activestyle="dotbox")
    sb2.config(command=listbox_sel.yview)
    listbox_sel.pack(side="left", fill="both", expand=True)
    sb2.pack(side="left", fill="y")
    lbl_contador = tk.Label(col_der, text="0 seleccionados",
                             font=("Arial", 8), fg="#555")
    lbl_contador.pack(anchor="w", pady=(3, 0))

    panel.columnconfigure(0, weight=1)
    panel.columnconfigure(2, weight=1)

    # ── Lógica ────────────────────────────────────────────────────────────────
    def actualizar_lista(*_):
        texto  = buscar_var.get().lower().strip()
        filtro = filtro_var.get()
        listbox.delete(0, tk.END)
        for s in TODOS_LOS_SIGNOS:
            if filtro == "Signos"   and not s.startswith("[Signo]"):   continue
            if filtro == "Síntomas" and not s.startswith("[Síntoma]"): continue
            if texto in s.lower():
                listbox.insert(tk.END, s)

    def agregar(event=None):
        sel = listbox.curselection()
        if not sel:
            return
        signo = listbox.get(sel[0])
        if signo == "Sin signos":
            signos_seleccionados.clear()
            listbox_sel.delete(0, tk.END)
            signos_seleccionados.append("Sin signos")
            listbox_sel.insert(tk.END, "Sin signos")
        elif signo not in signos_seleccionados:
            if "Sin signos" in signos_seleccionados:
                signos_seleccionados.remove("Sin signos")
                listbox_sel.delete(0, tk.END)
            signos_seleccionados.append(signo)
            listbox_sel.insert(tk.END, signo)
        _actualizar_contador()

    def quitar(event=None):
        sel = listbox_sel.curselection()
        if sel:
            idx = sel[0]
            signo = listbox_sel.get(idx)
            listbox_sel.delete(idx)
            if signo in signos_seleccionados:
                signos_seleccionados.remove(signo)
        elif signos_seleccionados:
            signos_seleccionados.pop()
            listbox_sel.delete(tk.END)
        _actualizar_contador()

    def _actualizar_contador():
        n = len(signos_seleccionados)
        lbl_contador.config(text=f"{n} seleccionado{'s' if n != 1 else ''}")

    def limpiar():
        signos_seleccionados.clear()
        listbox_sel.delete(0, tk.END)
        buscar_var.set("")
        actualizar_lista()
        _actualizar_contador()

    def get_signos() -> str:
        return ", ".join(signos_seleccionados) if signos_seleccionados else "Sin signos"

    # Botones centrales (después de definir las funciones)
    tk.Button(col_mid, text="➕", font=("Arial", 13), width=2, relief="flat",
              cursor="hand2", command=agregar).pack(pady=4)
    tk.Button(col_mid, text="✖", font=("Arial", 13), width=2, relief="flat",
              fg="#c0392b", cursor="hand2", command=quitar).pack(pady=4)
    tk.Button(col_mid, text="🗑", font=("Arial", 11), width=2, relief="flat",
              fg="#888", cursor="hand2", command=limpiar).pack(pady=4)

    buscar_var.trace_add("write", actualizar_lista)
    filtro_var.trace_add("write", actualizar_lista)
    listbox.bind("<Double-Button-1>", agregar)
    listbox_sel.bind("<Double-Button-1>", quitar)
    actualizar_lista()

    return get_signos, limpiar


# ── Ventana principal de registro ─────────────────────────────────────────────

def abrir_registro(ventana_root: tk.Tk, menu: tk.Toplevel) -> None:
    menu.withdraw()

    reg = tk.Toplevel(ventana_root)
    reg.title("Registro de Paciente")
    reg.resizable(True, True)
    agregar_firma(reg)
    aplicar_icono(reg)

    # Canvas con scroll para que funcione en pantallas pequeñas
    canvas = tk.Canvas(reg)
    vsb = tk.Scrollbar(reg, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame = tk.Frame(canvas, padx=24, pady=16)
    frame_id = canvas.create_window((0, 0), window=frame, anchor="nw")

    def _on_frame(e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    def _on_canvas(e):
        canvas.itemconfig(frame_id, width=e.width)
    frame.bind("<Configure>", _on_frame)
    canvas.bind("<Configure>", _on_canvas)

    def _scroll(event):
        if event.num == 4:
            canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas.yview_scroll(1, "units")
        else:
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    reg.bind_all("<MouseWheel>", _scroll)
    reg.bind_all("<Button-4>",   _scroll)
    reg.bind_all("<Button-5>",   _scroll)

    def _limpiar_scroll(e):
        reg.unbind_all("<MouseWheel>")
        reg.unbind_all("<Button-4>")
        reg.unbind_all("<Button-5>")
    reg.bind("<Destroy>", _limpiar_scroll)

    # ── Título ────────────────────────────────────────────────────────────────
    tk.Label(frame, text="Registro de Paciente",
             font=("Arial", 13, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 12))

    # ── Campos de texto ───────────────────────────────────────────────────────
    campos = [
        ("Nombre",           "nombre"),
        ("Edad (años)",      "edad"),
        ("Peso (kg)",        "peso"),
        ("Talla (m)",        "talla"),
        ("% Grasa corporal", "grasa"),
        ("% Masa muscular",  "musculo"),
    ]
    entries = {}
    for i, (label, key) in enumerate(campos, start=1):
        tk.Label(frame, text=label, anchor="w").grid(row=i, column=0, sticky="w", pady=4)
        e = tk.Entry(frame, width=34)
        e.grid(row=i, column=1, sticky="w", pady=4)
        entries[key] = e

    # ── Sexo ──────────────────────────────────────────────────────────────────
    fila_sexo = len(campos) + 1
    tk.Label(frame, text="Sexo", anchor="w").grid(row=fila_sexo, column=0, sticky="w", pady=4)
    sexo_var = tk.StringVar(value="")
    rf = tk.Frame(frame)
    rf.grid(row=fila_sexo, column=1, sticky="w", pady=4)
    tk.Radiobutton(rf, text="Masculino", variable=sexo_var, value="M",
                   font=("Arial", 10)).pack(side="left", padx=(0, 20))
    tk.Radiobutton(rf, text="Femenino",  variable=sexo_var, value="F",
                   font=("Arial", 10)).pack(side="left")

    # ── Signos / Síntomas ─────────────────────────────────────────────────────
    fila_signos = len(campos) + 2
    get_signos, limpiar_signos = crear_widget_signos(frame, fila_signos)

    # ── Resultado ─────────────────────────────────────────────────────────────
    fila_resultado = len(campos) + 3
    res_frame = tk.LabelFrame(frame, text="Resultado", padx=10, pady=8)
    res_frame.grid(row=fila_resultado, column=0, columnspan=2,
                   sticky="ew", pady=(10, 4))
    lbl_clasificacion = tk.Label(res_frame, text="—",
                                  font=("Arial", 12, "bold"), width=30)
    lbl_clasificacion.pack()
    lbl_justificacion = tk.Label(res_frame, text="", wraplength=560,
                                  justify="left", fg="#444")
    lbl_justificacion.pack()

    # ── Lógica de cálculo y guardado ──────────────────────────────────────────
    def calcular_y_mostrar() -> dict | None:
        try:
            nombre  = entries["nombre"].get().strip()
            edad    = int(entries["edad"].get())
            sexo    = sexo_var.get()
            peso    = float(entries["peso"].get())
            talla   = float(entries["talla"].get())
            grasa   = float(entries["grasa"].get())
            musculo = float(entries["musculo"].get())
            signos  = get_signos()

            if not nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío")
                return None
            if sexo not in ("M", "F"):
                messagebox.showerror("Error", "Debes seleccionar el sexo")
                return None

            imc = calcular_imc(peso, talla)
            res = clasificar_obesidad(imc, grasa, musculo, sexo, edad, signos)

            color = COLOR_CLASIFICACION.get(res["clasificacion"], "#000")
            lbl_clasificacion.config(text=res["clasificacion"], fg=color)
            lbl_justificacion.config(text=res["justificacion"])

            return {
                "nombre": nombre, "edad": edad, "sexo": sexo,
                "peso": peso, "talla": talla, "imc": round(imc, 2),
                "grasa": grasa, "musculo": musculo, "signos": signos,
                **res,
            }
        except ValueError as e:
            messagebox.showerror("Error de entrada", str(e))
            return None

    def guardar():
        datos = calcular_y_mostrar()
        if datos is None:
            return
        guardar_paciente(datos)
        mostrar_confirmacion(reg, datos["nombre"], datos)
        for e in entries.values():
            e.delete(0, tk.END)
        sexo_var.set("")
        limpiar_signos()
        lbl_clasificacion.config(text="—", fg="black")
        lbl_justificacion.config(text="")

    def volver():
        reg.destroy()
        menu.deiconify()

    # ── Botones ───────────────────────────────────────────────────────────────
    fila_botones = len(campos) + 4
    btn_frame = tk.Frame(frame)
    btn_frame.grid(row=fila_botones, column=0, columnspan=2, pady=12)

    tk.Button(btn_frame, text="Calcular clasificación",
              command=calcular_y_mostrar, width=22).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Guardar paciente",
              command=guardar, width=18).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Volver al menú",
              command=volver, width=14).pack(side="left", padx=6)

    reg.protocol("WM_DELETE_WINDOW", volver)
    reg.geometry("800x700")
    reg.update_idletasks()
