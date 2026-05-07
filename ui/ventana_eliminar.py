"""
ventana_eliminar.py — Ventana para eliminar un paciente por ID.
"""
import tkinter as tk
from tkinter import messagebox

from core.db import get_conexion, eliminar_paciente
from ui.ui_utils import agregar_firma, aplicar_icono

def abrir_eliminar_paciente(ventana_root: tk.Tk, menu: tk.Toplevel) -> None:
    ventana = tk.Toplevel(ventana_root)
    ventana.title("Eliminar Paciente")
    ventana.geometry("360x200")
    ventana.resizable(False, False)
    agregar_firma(ventana)
    aplicar_icono(ventana)
    
    tk.Label(ventana, text="Ingrese ID del paciente a eliminar:",
             font=("Arial", 11)).pack(pady=14)

    entry_id = tk.Entry(ventana, font=("Arial", 12), width=14, justify="center")
    entry_id.pack(pady=4)

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

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"Paciente ID {id_paciente} — {nombre}, {sexo_txt}, {edad} años\n"
            f"Clasificación: {clasif}\n\n¿Seguro que deseas eliminarlo?"
        )

        if confirmar:
            eliminar_paciente(id_paciente)
            messagebox.showinfo("Éxito", "Paciente eliminado correctamente")
            entry_id.delete(0, tk.END)

    def volver():
        ventana.destroy()
        menu.deiconify()

    btn_frame = tk.Frame(ventana)
    btn_frame.pack(pady=14)
    tk.Button(btn_frame, text="Eliminar", command=eliminar,
              bg="#e74c3c", fg="white", width=14).pack(side="left", padx=6)
    tk.Button(btn_frame, text="Volver al menú", command=volver,
              width=14).pack(side="left", padx=6)

    ventana.protocol("WM_DELETE_WINDOW", volver)
