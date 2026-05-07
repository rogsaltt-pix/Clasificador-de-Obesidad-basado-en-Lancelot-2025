"""
Módulo de lógica de clasificación de obesidad.
Basado en: Rubino et al. (2025). The Lancet Diabetes & Endocrinology.
Nueva clasificación: Sin Obesidad / Obesidad Preclínica / Obesidad Clínica
"""

# ── Rangos de referencia ──────────────────────────────────────────────────────

IMC_RANGOS = [
    (0,    18.5,  "Bajo peso"),
    (18.5, 25.0,  "Peso normal"),
    (25.0, 30.0,  "Sobrepeso"),
    (30.0, 35.0,  "Obesidad tipo 1"),
    (35.0, 40.0,  "Obesidad tipo 2"),
    (40.0, float("inf"), "Obesidad tipo 3"),
]

# % grasa corporal: saludable según sexo y grupo de edad
GRASA_REFERENCIA = {
    # sexo: [(edad_min, edad_max, min_saludable, max_saludable)]
    # M = Masculino, F = Femenino
    "M": [
        (0,  39,  10, 20),
        (40, 59,  11, 22),
        (60, 999, 13, 25),
    ],
    "F": [
        (0,  39,  20, 30),
        (40, 59,  23, 33),
        (60, 999, 24, 35),
    ],
}

# % masa muscular: adecuado según sexo
MUSCULO_MINIMO = {"M": 40, "F": 30}  # M=Masculino, F=Femenino

# Signos/síntomas que indican daño orgánico (obesidad clínica)
# Fuente: base de datos signosysintomas.sqlite + criterio Lancet 2025
SIGNOS_DANIO_ORGANICO = {
    # Metabólicos
    "hipertensión", "hipertension", "hiperglucemia", "hipoglucemia",
    "diabetes", "poliuria", "polidipsia", "polifagia", "nocturia", "disuria",
    "glicemia elevada", "glucosa elevada", "sed excesiva",
    "frecuencia urinaria aumentada", "orina oscura",
    # Cardiovasculares
    "arritmia", "soplo cardíaco", "soplo cardiaco", "ingurgitación yugular",
    "ingurgitacion yugular", "insuficiencia", "enfermedad coronaria", "infarto",
    "cardiopatía", "cardiopatia", "palpitaciones", "dolor torácico",
    "opresión en pecho", "opresion en pecho",
    # Respiratorios
    "apnea", "disnea", "ortopnea", "hemoptisis", "dificultad para respirar",
    "sensación de ahogo", "sensacion de ahogo",
    # Hepáticos / abdominales
    "hígado graso", "higado graso", "esteatosis", "hepatomegalia",
    "esplenomegalia", "ascitis", "ictericia",
    # Renales
    "hematuria", "anuria", "oliguria", "nefropatía", "nefropatia",
    # Neurológicos / funcionales
    "coma", "convulsiones", "parálisis", "paralisis", "hemiparesia",
    "disfagia", "visión borrosa", "vision borrosa", "pérdida de memoria",
    "perdida de memoria", "pérdida de audición", "perdida de audicion",
    "desmayo", "limitacion funcional", "limitación funcional",
    # Cutáneos / periféricos
    "cianosis", "edema pulmonar", "edema periférico", "edema periferico",
    "osteoporosis visible",
    # Musculoesqueléticos con impacto funcional
    "artritis", "fatiga", "dolor articular", "dolor lumbar",
    "aumento de peso", "sudoración nocturna", "sudoracion nocturna",
}

# Signos/síntomas de riesgo aumentado (sin daño orgánico establecido)
SIGNOS_RIESGO = {
    "triglicéridos", "trigliceridos", "colesterol", "prediabetes",
    "resistencia insulina", "resistencia a la insulina",
    "pérdida de fuerza", "perdida de fuerza", "fatiga postprandial",
    "fatiga crónica", "fatiga cronica", "dolor en extremidades",
    "dolor muscular", "debilidad", "insomnio", "ansiedad",
    "irritabilidad", "bajo rendimiento físico", "bajo rendimiento fisico",
    "cansancio matutino", "rigidez matutina", "hormigueo", "entumecimiento",
}


# ── Funciones auxiliares ──────────────────────────────────────────────────────

def calcular_imc(peso: float, talla: float) -> float:
    if talla <= 0:
        raise ValueError("La talla debe ser mayor a 0")
    if peso <= 0:
        raise ValueError("El peso debe ser mayor a 0")
    return peso / (talla ** 2)


def clasificar_imc(imc: float) -> str:
    for low, high, label in IMC_RANGOS:
        if low <= imc < high:
            return label
    return "Obesidad tipo 3"


def hay_exceso_grasa(porcentaje_grasa: float, sexo: str, edad: int) -> bool:
    """Retorna True si el % grasa está por encima del rango saludable."""
    rangos = GRASA_REFERENCIA.get(sexo.upper(), [])
    for edad_min, edad_max, minimo, maximo in rangos:
        if edad_min <= edad <= edad_max:
            return porcentaje_grasa >= maximo
    return False


def masa_muscular_baja(porcentaje_musculo: float, sexo: str) -> bool:
    return porcentaje_musculo < MUSCULO_MINIMO.get(sexo.upper(), 35)


def analizar_signos(signos_texto: str) -> tuple[bool, bool]:
    """
    Retorna (tiene_danio_organico, tiene_signos_riesgo).
    """
    texto = signos_texto.lower()
    danio = any(s in texto for s in SIGNOS_DANIO_ORGANICO)
    riesgo = any(s in texto for s in SIGNOS_RIESGO)
    return danio, riesgo


# ── Clasificación principal ───────────────────────────────────────────────────

def clasificar_obesidad(
    imc: float,
    porcentaje_grasa: float,
    porcentaje_musculo: float,
    sexo: str,
    edad: int,
    signos: str,
) -> dict:
    """
    Clasifica al paciente según el criterio Lancet 2025.

    Retorna un dict con:
        clasificacion: "Sin obesidad" | "Obesidad preclínica" | "Obesidad clínica"
        imc_label: etiqueta del IMC
        exceso_grasa: bool
        musculo_bajo: bool
        danio_organico: bool
        signos_riesgo: bool
        justificacion: str
    """
    imc_label = clasificar_imc(imc)
    exceso = hay_exceso_grasa(porcentaje_grasa, sexo, edad)
    musculo_bajo = masa_muscular_baja(porcentaje_musculo, sexo)
    danio, riesgo = analizar_signos(signos)

    # ── Lógica de clasificación ──
    # Obesidad clínica: exceso de grasa + daño en órganos/tejidos
    if exceso and danio:
        clasificacion = "Obesidad clínica"
        justificacion = (
            f"Presenta exceso de grasa corporal ({porcentaje_grasa}%) "
            f"con evidencia de daño orgánico/tisular ({signos}). "
            f"Su IMC indica {imc_label}."
        )

    # Obesidad clínica: daño orgánico confirmado (independiente del % grasa o IMC)
    # Ej: diabetes, hipertensión, hígado graso — son enfermedades activas
    elif danio:
        clasificacion = "Obesidad clínica"
        causa = "exceso de grasa corporal" if exceso else "composición corporal alterada"
        justificacion = (
            f"Daño orgánico/tisular confirmado ({signos}), compatible con obesidad clínica. "
            f"IMC: {imc_label}. % grasa: {porcentaje_grasa}% "
            f"({'por encima' if exceso else 'dentro'} del rango saludable). "
            f"La enfermedad activa es criterio suficiente para clasificación clínica."
        )

    # Obesidad preclínica: exceso de grasa sin daño orgánico establecido
    elif exceso and not danio:
        clasificacion = "Obesidad preclínica"
        extras = []
        if musculo_bajo:
            extras.append("masa muscular reducida")
        if riesgo:
            extras.append(f"signos de riesgo: {signos}")
        extra_txt = ("; " + ", ".join(extras)) if extras else ""
        justificacion = (
            f"Exceso de grasa corporal ({porcentaje_grasa}%) sin daño orgánico "
            f"establecido{extra_txt}. IMC: {imc_label}. "
            f"Función orgánica preservada pero con riesgo aumentado."
        )

    # Obesidad preclínica: IMC ≥30 sin daño orgánico
    elif imc >= 30 and not danio:
        clasificacion = "Obesidad preclínica"
        justificacion = (
            f"IMC de {imc:.1f} ({imc_label}) sin daño orgánico confirmado. "
            f"% grasa ({porcentaje_grasa}%) dentro de rangos. "
            f"Se clasifica como preclínica por IMC elevado."
        )

    # Sin obesidad
    else:
        clasificacion = "Sin obesidad"
        notas = []
        if imc >= 25:
            notas.append(f"IMC en {imc_label}")
        if musculo_bajo:
            notas.append("masa muscular por debajo del óptimo")
        if riesgo:
            notas.append(f"presenta: {signos} (monitorear)")
        notas_txt = ". Nota: " + "; ".join(notas) if notas else ""
        justificacion = (
            f"Sin exceso de grasa corporal confirmado y sin daño orgánico. "
            f"IMC: {imc_label}{notas_txt}."
        )

    return {
        "clasificacion": clasificacion,
        "imc_label": imc_label,
        "exceso_grasa": exceso,
        "musculo_bajo": musculo_bajo,
        "danio_organico": danio,
        "signos_riesgo": riesgo,
        "justificacion": justificacion,
    }
