import random
from pathlib import Path

archivos = [
    Path(r"D:\VS Code\Test_PPA\backend\main.py"),
    Path(r"D:\VS Code\Test_PPA\backend\pico_placa.py")
]

archivo = random.choice(archivos)

with open(archivo, "a", encoding="utf-8") as f:
    f.write("\n#*")

print(f"Modificado: {archivo.name}")