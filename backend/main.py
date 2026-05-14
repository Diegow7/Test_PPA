import os
import time
from collections import defaultdict, deque

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from pico_placa import puede_circular

# Crear app
app = FastAPI()

API_KEY = os.getenv("API_KEY")
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "30"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))

_rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)

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

def verificar_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key no configurada")

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="API key invalida")

    return x_api_key

def verificar_rate_limit(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    bucket = _rate_limit_buckets[client_ip]

    # Limpiar solicitudes fuera de la ventana
    while bucket and (now - bucket[0]) > RATE_LIMIT_WINDOW_SEC:
        bucket.popleft()

    if len(bucket) >= RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes, intenta mas tarde"
        )

    bucket.append(now)

# Ruta principal
@app.get("/")
def home():
    return FileResponse(frontend_dir / "index.html")

# Ruta para validar circulación
@app.post("/validar")
def validar_vehiculo(
    vehiculo: Vehiculo,
    _: str = Depends(verificar_api_key),
    __: None = Depends(verificar_rate_limit)
):

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