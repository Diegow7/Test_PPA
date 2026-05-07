from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from pico_placa import puede_circular

# Crear app
app = FastAPI()

frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Permitir conexión frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos
class Vehiculo(BaseModel):
    placa: str
    fecha: str
    hora: str

# Ruta principal
@app.get("/")
def home():
    return FileResponse(frontend_dir / "index.html")

# Ruta para validar circulación
@app.post("/validar")
def validar_vehiculo(vehiculo: Vehiculo):

    # Verificar circulación
    permitido = puede_circular(
        vehiculo.placa,
        vehiculo.fecha,
        vehiculo.hora
    )

    # Resultado texto
    resultado = (
        "Puede circular"
        if permitido
        else
        "No puede circular"
    )

    # Respuesta
    return {
        "placa": vehiculo.placa,
        "fecha": vehiculo.fecha,
        "hora": vehiculo.hora,
        "resultado": resultado
    }