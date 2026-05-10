"""
db.py — Conexión y gestión de la base de datos SQLite.
"""
import sqlite3
import os

DB_PATH = "database/pacientes.db"

def get_conexion() -> sqlite3.Connection:
    # Asegurar que el directorio existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def inicializar_db() -> None:
    con = get_conexion()
    
    # REESTRUCTURACIÓN COMPLETA:
    # Si la tabla ya existe con el esquema viejo, la renombramos para migrarla o empezar de cero
    # para asegurar que los nombres de las columnas tengan sentido clínico actual.
    
    con.execute("DROP TABLE IF EXISTS pacientes_old")
    
    # Verificar si existe la tabla actual para decidir si recrearla
    table_exists = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pacientes'").fetchone()
    
    if table_exists:
        # Si ya tiene la columna 'nivel_musculo', asumimos que ya está actualizada
        cols = [row[1] for row in con.execute("PRAGMA table_info(pacientes)").fetchall()]
        if "nivel_musculo" not in cols:
            con.execute("ALTER TABLE pacientes RENAME TO pacientes_old")
            table_exists = False

    if not table_exists:
        con.execute("""
            CREATE TABLE pacientes (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre              TEXT NOT NULL,
                edad                INTEGER,
                sexo                TEXT,
                peso                REAL,
                talla               REAL,
                imc                 REAL,
                exceso_grasa        TEXT, -- "Sí" / "No"
                nivel_musculo       TEXT, -- "Baja" / "Normal" / "Alta"
                signos_sintomas     TEXT,
                clasificacion_imc   TEXT,
                clasificacion_final TEXT,
                justificacion       TEXT,
                fecha_registro      DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Intentar migrar datos básicos si existía la tabla vieja
        try:
            old_exists = con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pacientes_old'").fetchone()
            if old_exists:
                con.execute("""
                    INSERT INTO pacientes (id, nombre, edad, sexo, peso, talla, imc, signos_sintomas, clasificacion_imc, clasificacion_final, justificacion)
                    SELECT id, nombre, edad, sexo, peso, talla, imc, signos_sintomas, clasificacion_imc, clasificacion_final, justificacion
                    FROM pacientes_old
                """)
                con.execute("DROP TABLE pacientes_old")
        except Exception:
            pass # Si falla la migración, empezamos con tabla limpia

    con.commit()
    con.close()

def guardar_paciente(datos: dict) -> None:
    """Inserta un paciente en la base de datos con el nuevo esquema cualitativo."""
    con = get_conexion()
    
    grasa_val = "Sí" if datos.get("exceso_grasa_bool", False) else "No"
    musculo_val = datos.get("musculo_label", "Normal")
    
    con.execute("""
        INSERT INTO pacientes (
            nombre, edad, sexo, peso, talla, imc,
            exceso_grasa, nivel_musculo, signos_sintomas,
            clasificacion_imc, clasificacion_final, justificacion
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        datos["nombre"], datos["edad"], datos["sexo"],
        datos["peso"], datos["talla"], datos["imc"],
        grasa_val, musculo_val, datos["signos"],
        datos["imc_label"], datos["clasificacion"], datos["justificacion"]
    ))
    con.commit()
    con.close()

def obtener_pacientes() -> list:
    """Devuelve los datos principales para la tabla de visualización."""
    con = get_conexion()
    rows = con.execute("""
        SELECT id, nombre, edad, sexo, peso, talla,
               ROUND(imc,2), exceso_grasa, nivel_musculo,
               signos_sintomas, clasificacion_final
        FROM pacientes
        ORDER BY id DESC
    """).fetchall()
    con.close()
    return rows

def obtener_paciente_por_id(id_paciente: int) -> tuple | None:
    """Devuelve todos los detalles de un paciente."""
    con = get_conexion()
    row = con.execute("""
        SELECT nombre, edad, sexo, peso, talla, ROUND(imc,2),
               exceso_grasa, nivel_musculo, signos_sintomas,
               clasificacion_imc, clasificacion_final, justificacion
        FROM pacientes WHERE id = ?
    """, (id_paciente,)).fetchone()
    con.close()
    return row

def eliminar_paciente(id_paciente: int) -> None:
    con = get_conexion()
    con.execute("DELETE FROM pacientes WHERE id = ?", (id_paciente,))
    con.commit()
    con.close()
