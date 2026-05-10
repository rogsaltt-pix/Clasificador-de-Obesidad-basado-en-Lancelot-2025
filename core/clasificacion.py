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

# Signos/síntomas que indican daño orgánico (obesidad clínica)
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

# Signos/síntomas de riesgo aumentado
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
    if talla <= 0: raise ValueError("La talla debe ser mayor a 0")
    if peso <= 0: raise ValueError("El peso debe ser mayor a 0")
    return peso / (talla ** 2)


def clasificar_imc(imc: float) -> str:
    for low, high, label in IMC_RANGOS:
        if low <= imc < high: return label
    return "Obesidad tipo 3"


def analizar_signos(signos_texto: str) -> tuple[bool, bool]:
    if not signos_texto or signos_texto.lower() == "sin signos":
        return False, False
    texto = signos_texto.lower()
    danio = any(s in texto for s in SIGNOS_DANIO_ORGANICO)
    riesgo = any(s in texto for s in SIGNOS_RIESGO)
    return danio, riesgo


# ── Clasificación principal ───────────────────────────────────────────────────

def clasificar_obesidad(
    imc: float,
    exceso_grasa: bool,
    musculo_label: str,
    sexo: str,
    edad: int,
    signos: str,
) -> dict:
    """
    Clasificación estricta basada en el nuevo paradigma Lancet 2025 y entradas cualitativas.
    """
    imc_label = clasificar_imc(imc)
    danio, riesgo = analizar_signos(signos)
    
    # Hay signos si hay daño o riesgo reportado
    tiene_signos = danio or riesgo

    # ── Lógica de la Tabla Lancet 2025 ──

    # CASO: NO HAY EXCESO DE GRASA (Casos 1, 2 y 4 de la tabla)
    if not exceso_grasa:
        clasificacion = "Sin obesidad"
        justificacion = (
            f"No se reporta exceso de grasa corporal. "
            f"Según el nuevo estándar Lancet 2025, la ausencia de exceso de adiposidad "
            f"descarta el diagnóstico de obesidad, incluso con un IMC de {imc:.1f} ({imc_label})."
        )
        if tiene_signos:
            justificacion += f" Nota: Los síntomas reportados ({signos}) deben evaluarse por otras causas."

    # CASO: SÍ HAY EXCESO DE GRASA
    else:
        # ¿Hay Signos y Síntomas? (Caso 6 de la tabla)
        if tiene_signos:
            clasificacion = "Obesidad clínica"
            justificacion = (
                f"Presenta exceso de grasa corporal y signos/síntomas clínicos asociados ({signos}). "
                f"Esto define un estado de obesidad clínica, independientemente de si el IMC es {imc:.1f} ({imc_label})."
            )
        
        # ¿No hay Signos y Síntomas? (Casos 3 y 5 de la tabla)
        else:
            clasificacion = "Obesidad preclínica"
            justificacion = (
                f"Presenta exceso de grasa corporal sin signos o síntomas clínicos detectables. "
                f"Se clasifica como obesidad preclínica por el riesgo metabólico latente. "
                f"IMC actual: {imc:.1f} ({imc_label})."
            )

    return {
        "clasificacion": clasificacion,
        "imc_label": imc_label,
        "exceso_grasa": exceso_grasa,
        "musculo_label": musculo_label,
        "musculo_bajo": musculo_label == "Baja",
        "danio_organico": danio,
        "signos_riesgo": riesgo,
        "justificacion": justificacion,
    }
