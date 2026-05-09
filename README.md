MyBocu. V0.1
Hecho por un estudiante de Nutrición y Dietética de la Universidad Nacional de Colombia, Bogotá.

Basado en The Lancet Diabetes & Endocrinology. (2025). Redefining obesity: advancing care for better lives. Disponible en: https://www.thelancet.com/journals/landia/article/PIIS2213-8587(25)00004-X/fulltext

La obesidad ya no se debe diagnosticar por IMC exclusivamente, ahora existen parametros y datos que nos guiarán a una diagnostico preciso de esta enfermedad crónica no transmisible. Desde hace un año he estado pensando en crear una herramienta que me permitiera almacenar datos, analizarlos y automatizar resultados. En marzo de 2026 se creó la idea de MyBocu. V0.1. Esta herramienta tiene la capacidad de diagnosticar obesidad clinica o pre-clinica basandose en los datos suministrados por el profesional de la salud encargado.

Ciencia bajo la evidencia.

#ESTRUCTURA

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
