# Sistema de Clasificación de Obesidad

Aplicación desarrollada en Python para el registro, evaluación y clasificación de pacientes según criterios modernos de obesidad clínica y preclínica basados en composición corporal, IMC y signos clínicos.

El proyecto está orientado al área de Nutrición y Dietética, permitiendo almacenar pacientes, analizar indicadores antropométricos y generar clasificaciones clínicas de forma automatizada mediante una interfaz gráfica intuitiva.

---

# Características principales

- Registro completo de pacientes
- Cálculo automático de IMC
- Evaluación de porcentaje de grasa corporal
- Evaluación de masa muscular
- Clasificación:
  - Sin obesidad
  - Obesidad preclínica
  - Obesidad clínica
- Detección de daño orgánico y signos de riesgo
- Sistema visual con colores por clasificación
- Base de datos SQLite integrada
- Visualización detallada de pacientes
- Eliminación segura de registros
- Arquitectura modular y escalable
- Interfaz gráfica desarrollada con Tkinter

---

# Criterios clínicos implementados

La lógica de clasificación está basada en:

> Rubino et al. (2025). *The Lancet Diabetes & Endocrinology*

El sistema considera:

- IMC (Índice de Masa Corporal)
- Porcentaje de grasa corporal
- Masa muscular
- Signos y síntomas clínicos
- Evidencia de daño orgánico o funcional

---

# Tecnologías utilizadas

- Python
- Tkinter
- SQLite
- Git & GitHub

---

# Estructura del proyecto

```text
PROYECTO_GIT/
│
├── main.py
│
├── assets/
│   ├── icon.ico
│   ├── icon.png
│   └── logo.png
│
├── core/
│   ├── clasificacion.py
│   ├── constantes.py
│   └── db.py
│
├── database/
│   ├── pacientes.db
│   └── signosysintomas.sqlite
│
├── ui/
│   ├── ui_utils.py
│   ├── ventana_registro.py
│   ├── ventana_visualizar.py
│   └── ventana_eliminar.py
│
└── README.md