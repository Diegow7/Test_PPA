import random
from pathlib import Path
from datetime import datetime

# Archivos candidatos
archivos = [
    Path(r"D:\VS Code\Test_PPA\backend\main.py"),
    Path(r"D:\VS Code\Test_PPA\backend\pico_placa.py")
]

# Tipos de commit
tipos = [
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "test",
    "chore"
]

# Descripciones
descripciones = [
    "add plate validation helper",
    "improve search performance",
    "handle null values in requests",
    "prevent duplicate records",
    "update README examples",
    "improve endpoint documentation",
    "normalize code indentation",
    "apply formatting cleanup",
    "simplify validation logic",
    "extract reusable methods",
    "add unit tests for validators",
    "improve coverage for API routes",
    "update repository structure",
    "clean temporary files",
    "optimize code flow",
    "improve code quality",
    "update validation logic",
    "reorganize project files",
    "adjust helper functions",
    "enhance test coverage"
]

# Fecha actual
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Selección aleatoria
archivo = random.choice(archivos)

# Cambio único dentro del archivo
with open(archivo, "a", encoding="utf-8") as f:
    f.write(
        f"\n# AutoUpdate {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

# Commit único
mensaje = (
    f"{random.choice(tipos)}: "
    f"{random.choice(descripciones)} "
    f"[{timestamp}]"
)

# Guardar mensaje para el BAT
with open("commit_message.txt", "w", encoding="utf-8") as f:
    f.write(mensaje)

print(f"Archivo modificado: {archivo.name}")
print(f"Commit generado: {mensaje}")