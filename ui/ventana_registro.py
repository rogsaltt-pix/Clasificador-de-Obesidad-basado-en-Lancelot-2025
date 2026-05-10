"""
ventana_registro.py — Formulario de registro de nuevos pacientes.
"""
import tkinter as tk
from tkinter import messagebox

from core.constantes import COLOR_CLASIFICACION, TODOS_LOS_SIGNOS
from core.clasificacion import calcular_imc, clasificar_obesidad
from core.db import guardar_paciente
from ui.ui_utils import aplicar_icono, get_tema


# ── Confirmación ──────────────────────────────────────────────────────────────

def mostrar_confirmacion(parent, nombre, resultado):
    t     = get_tema()
    color = COLOR_CLASIFICACION.get(resultado["clasificacion"], "#333")

    win = tk.Toplevel(parent)
    win.title("Paciente guardado")
    win.geometry("720x600") # Altura más moderada
    win.resizable(True, True)
    win.configure(bg=t["bg"])
    win.grab_set()
    aplicar_icono(win)

    # Encabezado
    hf = tk.Frame(win, bg="#16A34A", pady=10)
    hf.pack(fill="x")
    tk.Label(hf, text="✔  Paciente guardado correctamente",
             font=("Segoe UI", 12, "bold"), bg="#16A34A", fg="white").pack()

    # Contenedor con scroll por si la pantalla es muy pequeña
    cv = tk.Canvas(win, bg=t["bg"], highlightthickness=0)
    vs = tk.Scrollbar(win, orient="vertical", command=cv.yview)
    cv.configure(yscrollcommand=vs.set)
    vs.pack(side="right", fill="y")
    cv.pack(side="left", fill="both", expand=True)

    body = tk.Frame(cv, padx=28, pady=16, bg=t["bg"])
    cv.create_window((0, 0), window=body, anchor="nw")
    body.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))

    for i, (lbl, val) in enumerate([
        ("Nombre:",          nombre),
        ("IMC:",             resultado["imc_label"]),
        ("Exceso de grasa:", "Sí" if resultado["exceso_grasa"] else "No"),
        ("Masa muscular:",   resultado["musculo_label"]),
    ]):
        tk.Label(body, text=lbl, font=("Segoe UI", 10, "bold"),
                 anchor="w", bg=t["bg"], fg=t["fg"]).grid(row=i, column=0, sticky="w", pady=3)
        tk.Label(body, text=val, anchor="w",
                 bg=t["bg"], fg=t["fg"]).grid(row=i, column=1, sticky="w", pady=3, padx=8)

    cf = tk.Frame(body, bg=color, pady=10, padx=12)
    cf.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(12, 4))
    tk.Label(cf, text="Clasificación:", font=("Segoe UI", 10),
             bg=color, fg="white").pack(side="left")
    tk.Label(cf, text=resultado["clasificacion"], font=("Segoe UI", 11, "bold"),
             bg=color, fg="white").pack(side="left", padx=8)

    tk.Button(body, text="Aceptar", command=win.destroy, width=16,
              font=("Segoe UI", 10, "bold"), bg="#3B82F6", fg="white",
              relief="flat", cursor="hand2", activebackground="#2563EB").grid(row=5, column=0, columnspan=2, pady=20)

    win.transient(parent)
    parent.wait_window(win)


# ── Widget Signos/Síntomas ────────────────────────────────────────────────────

def crear_widget_signos(frame, fila):
    t = get_tema()
    signos_seleccionados = []

    panel = tk.LabelFrame(frame, text="Signos / Síntomas",
                          padx=8, pady=8, font=("Segoe UI", 10, "bold"),
                          bg=t["bg"], fg=t["fg"])
    panel.grid(row=fila, column=0, columnspan=2, sticky="ew", pady=(10, 4))

    # Izquierda
    col_izq = tk.Frame(panel, bg=t["bg"])
    col_izq.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

    tk.Label(col_izq, text="Buscar:", font=("Segoe UI", 9, "bold"),
             bg=t["bg"], fg=t["fg"]).pack(anchor="w")
    buscar_var = tk.StringVar()
    tk.Entry(col_izq, textvariable=buscar_var, width=28,
             font=("Segoe UI", 10), bg=t["entry_bg"], fg=t["entry_fg"],
             relief="flat", highlightbackground=t["border"],
             highlightthickness=1).pack(fill="x", pady=(2, 4))

    filtro_var = tk.StringVar(value="Todos")
    ff = tk.Frame(col_izq, bg=t["bg"])
    ff.pack(anchor="w", pady=(0, 4))
    for op in ("Todos", "Síntomas"):
        tk.Radiobutton(ff, text=op, variable=filtro_var, value=op,
                       font=("Segoe UI", 8), bg=t["bg"], fg=t["fg"],
                       selectcolor=t["entry_bg"],
                       activebackground=t["bg"]).pack(side="left")

    lf1 = tk.Frame(col_izq, bg=t["bg"])
    lf1.pack(fill="both", expand=True)
    sb1 = tk.Scrollbar(lf1)
    listbox = tk.Listbox(lf1, height=7, width=25, yscrollcommand=sb1.set,
                         selectmode="single", exportselection=False,
                         font=("Segoe UI", 9), activestyle="dotbox",
                         cursor="hand2", bg=t["entry_bg"], fg=t["entry_fg"],
                         selectbackground=t["sel_bg"])
    sb1.config(command=listbox.yview)
    listbox.pack(side="left", fill="both", expand=True)
    sb1.pack(side="left", fill="y")

    # Centro
    col_mid = tk.Frame(panel, bg=t["bg"])
    col_mid.grid(row=0, column=1, padx=4, sticky="ns")
    tk.Label(col_mid, text="", bg=t["bg"]).pack(pady=10)

    # Derecha
    col_der = tk.Frame(panel, bg=t["bg"])
    col_der.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
    tk.Label(col_der, text="Seleccionados:", font=("Segoe UI", 9, "bold"),
             bg=t["bg"], fg=t["fg"]).pack(anchor="w")
    lf2 = tk.Frame(col_der, bg=t["bg"])
    lf2.pack(fill="both", expand=True, pady=(4, 0))
    sb2 = tk.Scrollbar(lf2)
    listbox_sel = tk.Listbox(lf2, height=7, width=25, yscrollcommand=sb2.set,
                              selectmode="single", exportselection=False,
                              font=("Segoe UI", 9), activestyle="dotbox",
                              bg="#0D3321" if t["bg"] == "#0F172A" else "#f0f7f0",
                              fg=t["entry_fg"])
    sb2.config(command=listbox_sel.yview)
    listbox_sel.pack(side="left", fill="both", expand=True)
    sb2.pack(side="left", fill="y")

    panel.columnconfigure(0, weight=1)
    panel.columnconfigure(2, weight=1)

    def actualizar_lista(*_):
        texto  = buscar_var.get().lower().strip()
        filtro = filtro_var.get()
        listbox.delete(0, tk.END)
        for s in TODOS_LOS_SIGNOS:
            if filtro == "Síntomas" and not s.startswith("[Síntoma]"): continue
            if texto in s.lower():
                listbox.insert(tk.END, s)

    def agregar(event=None):
        sel = listbox.curselection()
        if not sel: return
        signo = listbox.get(sel[0])
        if signo == "Sin signos":
            signos_seleccionados.clear(); listbox_sel.delete(0, tk.END)
            signos_seleccionados.append("Sin signos"); listbox_sel.insert(tk.END, "Sin signos")
        elif signo not in signos_seleccionados:
            if "Sin signos" in signos_seleccionados:
                signos_seleccionados.remove("Sin signos"); listbox_sel.delete(0, tk.END)
            signos_seleccionados.append(signo); listbox_sel.insert(tk.END, signo)

    def quitar(event=None):
        sel = listbox_sel.curselection()
        if sel:
            idx = sel[0]; signo = listbox_sel.get(idx)
            listbox_sel.delete(idx)
            if signo in signos_seleccionados: signos_seleccionados.remove(signo)
        elif signos_seleccionados:
            signos_seleccionados.pop(); listbox_sel.delete(tk.END)

    def limpiar():
        signos_seleccionados.clear(); listbox_sel.delete(0, tk.END)
        buscar_var.set(""); actualizar_lista()

    def get_signos():
        return ", ".join(signos_seleccionados) if signos_seleccionados else "Sin signos"

    # Botones centrales reducidos
    for txt, color, cmd in [("➕","#16A34A",agregar),("✖","#EF4444",quitar),("🗑","#64748B",limpiar)]:
        tk.Button(col_mid, text=txt, font=("Segoe UI", 11), width=2, relief="flat",
                  cursor="hand2", bg=color, fg="white",
                  activebackground="#1E293B", command=cmd).pack(pady=2)

    # --- Lógica de scroll independiente para las listas ---
    def _on_mousewheel(event):
        widget = event.widget
        if isinstance(widget, tk.Listbox):
            if event.num == 4 or event.delta > 0:
                widget.yview_scroll(-1, "units")
            else:
                widget.yview_scroll(1, "units")
            return "break"

    listbox.bind("<MouseWheel>", _on_mousewheel)
    listbox_sel.bind("<MouseWheel>", _on_mousewheel)
    listbox.bind("<Button-4>", _on_mousewheel)
    listbox.bind("<Button-5>", _on_mousewheel)
    listbox_sel.bind("<Button-4>", _on_mousewheel)
    listbox_sel.bind("<Button-5>", _on_mousewheel)

    buscar_var.trace_add("write", actualizar_lista)
    filtro_var.trace_add("write", actualizar_lista)
    listbox.bind("<Double-Button-1>", agregar)
    listbox_sel.bind("<Double-Button-1>", quitar)
    actualizar_lista()
    return get_signos, limpiar


# ── Ventana de registro ───────────────────────────────────────────────────────

def abrir_registro(ventana_root, menu):
    menu.withdraw()
    t = get_tema()

    reg = tk.Toplevel(ventana_root)
    reg.title("Registro de Paciente")
    reg.geometry("860x700") 
    reg.resizable(True, True)
    reg.configure(bg=t["bg"])
    aplicar_icono(reg)

    reg.rowconfigure(1, weight=1) 
    reg.columnconfigure(0, weight=1)

    # 1. Encabezado
    hf = tk.Frame(reg, bg=t["bg_header"], pady=10)
    hf.grid(row=0, column=0, sticky="ew")
    tk.Label(hf, text="➕  Registro de Paciente",
             font=("Segoe UI", 13, "bold"),
             bg=t["bg_header"], fg="white").pack(side="left", padx=20)
    tk.Label(hf, text="© rogsaltt-pix",
             font=("Segoe UI", 8, "italic"),
             fg="#94A3B8", bg=t["bg_header"]).pack(side="right", padx=16)

    # 2. Área Central con Scroll
    content_container = tk.Frame(reg, bg=t["bg"])
    content_container.grid(row=1, column=0, sticky="nsew")
    
    canvas = tk.Canvas(content_container, bg=t["bg"], highlightthickness=0)
    vsb = tk.Scrollbar(content_container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    frame = tk.Frame(canvas, padx=24, pady=10, bg=t["bg"])
    fid = canvas.create_window((0, 0), window=frame, anchor="nw")
    
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(fid, width=e.width))

    def _scroll_canvas(event):
        widget = reg.winfo_containing(event.x_root, event.y_root)
        if not isinstance(widget, tk.Listbox):
            if event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")
            else:
                canvas.yview_scroll(1, "units")

    reg.bind_all("<MouseWheel>", _scroll_canvas)
    reg.bind_all("<Button-4>",   _scroll_canvas)
    reg.bind_all("<Button-5>",   _scroll_canvas)
    
    reg.bind("<Destroy>", lambda e: [reg.unbind_all("<MouseWheel>"),
                                      reg.unbind_all("<Button-4>"),
                                      reg.unbind_all("<Button-5>")])

    # Campos Numéricos
    campos_num = [("Nombre","nombre"),("Edad (años)","edad"),("Peso (kg)","peso"),("Talla (m)","talla")]
    entries = {}
    for i, (label, key) in enumerate(campos_num, start=1):
        tk.Label(frame, text=label, anchor="w", bg=t["bg"], fg=t["fg"],
                 font=("Segoe UI", 10)).grid(row=i, column=0, sticky="w", pady=4)
        e = tk.Entry(frame, width=34, bg=t["entry_bg"], fg=t["entry_fg"],
                     font=("Segoe UI", 10), relief="flat",
                     highlightbackground=t["border"], highlightthickness=1,
                     insertbackground=t["fg"])
        e.grid(row=i, column=1, sticky="w", pady=4, padx=(8, 0))
        entries[key] = e

    # Sexo
    fila_sexo = len(campos_num) + 1
    tk.Label(frame, text="Sexo", anchor="w", bg=t["bg"], fg=t["fg"],
             font=("Segoe UI", 10)).grid(row=fila_sexo, column=0, sticky="w", pady=4)
    sexo_var = tk.StringVar(value="")
    rf_sexo = tk.Frame(frame, bg=t["bg"])
    rf_sexo.grid(row=fila_sexo, column=1, sticky="w", pady=4, padx=(8, 0))
    for txt, val in [("Masculino", "M"), ("Femenino", "F")]:
        tk.Radiobutton(rf_sexo, text=txt, variable=sexo_var, value=val,
                       font=("Segoe UI", 10), bg=t["bg"], fg=t["fg"],
                       selectcolor=t["entry_bg"],
                       activebackground=t["bg"]).pack(side="left", padx=(0, 16))

    # Exceso de Grasa (Cualitativo)
    fila_grasa = fila_sexo + 1
    tk.Label(frame, text="Exceso de grasa corporal", anchor="w", bg=t["bg"], fg=t["fg"],
             font=("Segoe UI", 10)).grid(row=fila_grasa, column=0, sticky="w", pady=4)
    grasa_var = tk.BooleanVar(value=False)
    rf_grasa = tk.Frame(frame, bg=t["bg"])
    rf_grasa.grid(row=fila_grasa, column=1, sticky="w", pady=4, padx=(8, 0))
    for txt, val in [("Sí", True), ("No", False)]:
        tk.Radiobutton(rf_grasa, text=txt, variable=grasa_var, value=val,
                       font=("Segoe UI", 10), bg=t["bg"], fg=t["fg"],
                       selectcolor=t["entry_bg"],
                       activebackground=t["bg"]).pack(side="left", padx=(0, 16))

    # Masa Muscular (Cualitativo)
    fila_musculo = fila_grasa + 1
    tk.Label(frame, text="Masa muscular", anchor="w", bg=t["bg"], fg=t["fg"],
             font=("Segoe UI", 10)).grid(row=fila_musculo, column=0, sticky="w", pady=4)
    musculo_var = tk.StringVar(value="Normal")
    rf_musculo = tk.Frame(frame, bg=t["bg"])
    rf_musculo.grid(row=fila_musculo, column=1, sticky="w", pady=4, padx=(8, 0))
    for txt in ["Baja", "Normal", "Alta"]:
        tk.Radiobutton(rf_musculo, text=txt, variable=musculo_var, value=txt,
                       font=("Segoe UI", 10), bg=t["bg"], fg=t["fg"],
                       selectcolor=t["entry_bg"],
                       activebackground=t["bg"]).pack(side="left", padx=(0, 16))

    # Signos
    get_signos, limpiar_signos = crear_widget_signos(frame, fila_musculo + 1)

    # Resultado
    res_frame = tk.LabelFrame(frame, text="Resultado", padx=12, pady=8,
                               bg=t["bg"], fg=t["fg"], font=("Segoe UI", 10, "bold"))
    res_frame.grid(row=fila_musculo + 2, column=0, columnspan=2,
                   sticky="ew", pady=(10, 4))
    lbl_clasif = tk.Label(res_frame, text="—", font=("Segoe UI", 12, "bold"),
                           width=30, bg=t["bg"], fg=t["fg"])
    lbl_clasif.pack()
    lbl_just = tk.Label(res_frame, text="", wraplength=560,
                         justify="left", fg=t["fg_sub"],
                         font=("Segoe UI", 9), bg=t["bg"])
    lbl_just.pack()

    # 3. Panel de Botones
    bf = tk.Frame(reg, bg=t["bg"], pady=12, highlightbackground=t["border"], highlightthickness=1)
    bf.grid(row=2, column=0, sticky="ew")

    def calcular_y_mostrar():
        try:
            nombre  = entries["nombre"].get().strip()
            edad    = int(entries["edad"].get())
            sexo    = sexo_var.get()
            peso    = float(entries["peso"].get())
            talla   = float(entries["talla"].get())
            grasa   = grasa_var.get()
            musculo = musculo_var.get()
            signos  = get_signos()
            
            if not nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío"); return None
            if sexo not in ("M", "F"):
                messagebox.showerror("Error", "Debes seleccionar el sexo"); return None
            
            imc = calcular_imc(peso, talla)
            # Pasamos los valores cualitativos directamente
            res = clasificar_obesidad(imc, grasa, musculo, sexo, edad, signos)
            
            color = COLOR_CLASIFICACION.get(res["clasificacion"], "#000")
            lbl_clasif.config(text=res["clasificacion"], fg=color)
            lbl_just.config(text=res["justificacion"])
            canvas.update_idletasks()
            canvas.yview_moveto(1.0) 
            
            return {"nombre":nombre,"edad":edad,"sexo":sexo,"peso":peso,
                    "talla":talla,"imc":round(imc,2),
                    "exceso_grasa_bool":grasa, "musculo_label":musculo,
                    "signos":signos,**res}
        except ValueError as e:
            messagebox.showerror("Error de entrada", "Asegúrate de llenar correctamente los campos numéricos."); return None

    def guardar():
        datos = calcular_y_mostrar()
        if datos is None: return
        guardar_paciente(datos)
        mostrar_confirmacion(reg, datos["nombre"], datos)
        for e in entries.values(): e.delete(0, tk.END)
        sexo_var.set("")
        grasa_var.set(False)
        musculo_var.set("Normal")
        limpiar_signos()
        lbl_clasif.config(text="—", fg=t["fg"])
        lbl_just.config(text="")
        canvas.yview_moveto(0.0)

    def volver():
        reg.destroy(); menu.deiconify()

    bc = tk.Frame(bf, bg=t["bg"])
    bc.pack()
    for txt, cmd, bg in [
        ("📊 Calcular", calcular_y_mostrar, "#3B82F6"),
        ("💾 Guardar",  guardar,            "#16A34A"),
        ("↩ Volver",   volver,             "#64748B"),
    ]:
        tk.Button(bc, text=txt, command=cmd, bg=bg, fg="white",
                  font=("Segoe UI", 10), relief="flat", cursor="hand2",
                  padx=12, pady=6, activebackground="#1E293B",
                  activeforeground="white").pack(side="left", padx=8)

    reg.protocol("WM_DELETE_WINDOW", volver)
