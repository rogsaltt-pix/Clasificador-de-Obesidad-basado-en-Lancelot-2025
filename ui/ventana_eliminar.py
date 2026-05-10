"""
ventana_eliminar.py — Ventana para eliminar un paciente por ID.
"""
import tkinter as tk
from tkinter import messagebox

from core.db import get_conexion, eliminar_paciente
from ui.ui_utils import aplicar_icono, get_tema


def abrir_eliminar_paciente(ventana_root: tk.Tk, menu: tk.Toplevel) -> None:
    t = get_tema()

    ventana = tk.Toplevel(ventana_root)
    ventana.title("Eliminar Paciente")
    ventana.geometry("380x240")
    ventana.resizable(False, False)
    ventana.configure(bg=t["bg"])
    aplicar_icono(ventana)

    # Encabezado
    hf = tk.Frame(ventana, bg="#7F1D1D", pady=12)
    hf.pack(fill="x")
    tk.Label(hf, text="🗑  Eliminar Paciente",
             font=("Segoe UI", 12, "bold"),
             bg="#7F1D1D", fg="white").pack()

    body = tk.Frame(ventana, bg=t["bg"], padx=30, pady=16)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Ingrese el ID del paciente a eliminar:",
             font=("Segoe UI", 10), bg=t["bg"], fg=t["fg"]).pack(pady=(0, 8))

    entry_id = tk.Entry(body, font=("Segoe UI", 13), width=10,
                        justify="center", bg=t["entry_bg"], fg=t["entry_fg"],
                        relief="flat", highlightbackground=t["border"],
                        highlightthickness=1, insertbackground=t["fg"])
    entry_id.pack()

    def eliminar():
        try:
            id_paciente = int(entry_id.get())
        except ValueError:
            messagebox.showerror("Error", "Debes ingresar un número válido")
            return

        con = get_conexion()
        cur = con.cursor()
        cur.execute(
            "SELECT id, nombre, edad, sexo, clasificacion_final FROM pacientes WHERE id = ?",
            (id_paciente,)
        )
        paciente = cur.fetchone()
        con.close()

        if paciente is None:
            messagebox.showerror("Error", f"No existe un paciente con ID {id_paciente}")
            return

        _, nombre, edad, sexo, clasif = paciente
        sexo_txt = "Masculino" if sexo == "M" else "Femenino"

        if messagebox.askyesno(
            "Confirmar eliminación",
            f"ID {id_paciente} — {nombre}, {sexo_txt}, {edad} años\n"
            f"Clasificación: {clasif}\n\n¿Seguro que deseas eliminarlo?"
        ):
            eliminar_paciente(id_paciente)
            messagebox.showinfo("Éxito", "Paciente eliminado correctamente")
            entry_id.delete(0, tk.END)

    def volver():
        ventana.destroy()
        menu.deiconify()

    bf = tk.Frame(body, bg=t["bg"])
    bf.pack(pady=16)

    tk.Button(bf, text="Eliminar", command=eliminar,
              bg="#EF4444", fg="white", font=("Segoe UI", 10),
              relief="flat", cursor="hand2", width=12, pady=6,
              activebackground="#DC2626").pack(side="left", padx=6)
    tk.Button(bf, text="Volver al menú", command=volver,
              bg=t["btn_bg"], fg=t["fg"], font=("Segoe UI", 10),
              relief="flat", cursor="hand2", width=14, pady=6,
              activebackground=t["border"]).pack(side="left", padx=6)

    # Firma
    tk.Label(ventana, text="© rogsaltt-pix",
             font=("Segoe UI", 8, "italic"),
             fg="#94A3B8", bg=t["bg_header"]).pack(side="bottom", pady=4, fill="x")

    ventana.protocol("WM_DELETE_WINDOW", volver)
