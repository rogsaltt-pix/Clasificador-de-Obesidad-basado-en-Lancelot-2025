"""
db.py — Conexión y gestión de la base de datos SQLite.
"""
import sqlite3

DB_PATH = "pacientes.db"


def get_conexion() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def inicializar_db() -> None:
    con = get_conexion()

    # Crear tabla si no existe
    con.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre              TEXT,
            edad                INTEGER,
            sexo                TEXT,
            peso                REAL,
            talla               REAL,
            imc                 REAL,
            porcentaje_grasa    REAL,
            porcentaje_musculo  REAL,
            signos_sintomas     TEXT,
            clasificacion_imc   TEXT,
            exceso_grasa        INTEGER,
            musculo_bajo        INTEGER,
            danio_organico      INTEGER,
            clasificacion_final TEXT,
            justificacion       TEXT
        )
    """)

    # Migración: agregar columnas nuevas si ya existía la tabla sin ellas
    columnas_necesarias = {
        "nombre":              "TEXT",
        "porcentaje_grasa":    "REAL",
        "porcentaje_musculo":  "REAL",
        "signos_sintomas":     "TEXT",
        "clasificacion_imc":   "TEXT",
        "exceso_grasa":        "INTEGER",
        "musculo_bajo":        "INTEGER",
        "danio_organico":      "INTEGER",
        "clasificacion_final": "TEXT",
        "justificacion":       "TEXT",
    }
    existentes = {row[1] for row in con.execute("PRAGMA table_info(pacientes)")}
    for col, tipo in columnas_necesarias.items():
        if col not in existentes:
            con.execute(f"ALTER TABLE pacientes ADD COLUMN {col} {tipo}")

    # Migración: eliminar CHECK constraints antiguos recreando la tabla sin ellos
    schema = con.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='pacientes'"
    ).fetchone()
    if schema and "CHECK" in schema[0]:
        con.executescript("""
            PRAGMA foreign_keys = OFF;
            ALTER TABLE pacientes RENAME TO pacientes_old;
            CREATE TABLE pacientes (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre              TEXT,
                edad                INTEGER,
                sexo                TEXT,
                peso                REAL,
                talla               REAL,
                imc                 REAL,
                porcentaje_grasa    REAL,
                porcentaje_musculo  REAL,
                signos_sintomas     TEXT,
                clasificacion_imc   TEXT,
                exceso_grasa        INTEGER,
                musculo_bajo        INTEGER,
                danio_organico      INTEGER,
                clasificacion_final TEXT,
                justificacion       TEXT
            );
            INSERT INTO pacientes (id, nombre, edad, sexo, peso, talla, imc,
                porcentaje_grasa, porcentaje_musculo, signos_sintomas,
                clasificacion_imc, exceso_grasa, musculo_bajo,
                danio_organico, clasificacion_final, justificacion)
            SELECT id, nombre, edad, sexo, peso, talla, imc,
                porcentaje_grasa, porcentaje_musculo, signos_sintomas,
                clasificacion_imc, exceso_grasa, musculo_bajo,
                danio_organico, clasificacion_final, justificacion
            FROM pacientes_old;
            DROP TABLE pacientes_old;
            PRAGMA foreign_keys = ON;
        """)

    con.commit()
    con.close()


def guardar_paciente(datos: dict) -> None:
    """Inserta un paciente en la base de datos."""
    con = get_conexion()
    con.execute("""
        INSERT INTO pacientes (
            nombre, edad, sexo, peso, talla, imc,
            porcentaje_grasa, porcentaje_musculo, signos_sintomas,
            clasificacion_imc, exceso_grasa, musculo_bajo,
            danio_organico, clasificacion_final, justificacion
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        datos["nombre"], datos["edad"], datos["sexo"],
        datos["peso"], datos["talla"], datos["imc"],
        datos["grasa"], datos["musculo"], datos["signos"],
        datos["imc_label"], datos["exceso_grasa"],
        datos["musculo_bajo"], datos["danio_organico"],
        datos["clasificacion"], datos["justificacion"],
    ))
    con.commit()
    con.close()


def obtener_pacientes() -> list:
    """Devuelve todos los pacientes para la tabla."""
    con = get_conexion()
    rows = con.execute("""
        SELECT id, nombre, edad, sexo, peso, talla,
               ROUND(imc,2), porcentaje_grasa, porcentaje_musculo,
               signos_sintomas, clasificacion_imc,
               exceso_grasa, musculo_bajo, danio_organico,
               clasificacion_final
        FROM pacientes
    """).fetchall()
    con.close()
    return rows


def obtener_paciente_por_id(id_paciente: int) -> tuple | None:
    """Devuelve todos los datos de un paciente por ID."""
    con = get_conexion()
    row = con.execute("""
        SELECT nombre, edad, sexo, peso, talla, ROUND(imc,2),
               porcentaje_grasa, porcentaje_musculo, signos_sintomas,
               clasificacion_imc, exceso_grasa, musculo_bajo,
               danio_organico, clasificacion_final, justificacion
        FROM pacientes WHERE id = ?
    """, (id_paciente,)).fetchone()
    con.close()
    return row


def eliminar_paciente(id_paciente: int) -> None:
    con = get_conexion()
    con.execute("DELETE FROM pacientes WHERE id = ?", (id_paciente,))
    con.commit()
    con.close()
