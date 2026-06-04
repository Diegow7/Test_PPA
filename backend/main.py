import os
import time
from collections import defaultdict, deque
from datetime import datetime

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path

from pico_placa import puede_circular, obtener_info_placa, validar_entrada, _puede_circular

# Crear app
app = FastAPI()

API_KEY = os.getenv("API_KEY")
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "30"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "20"))

def _parse_prefijos(valor):
    if not valor:
        return []

    return [
        item.strip().upper()
        for item in valor.split(",")
        if item.strip()
    ]

PREFIJOS_CARRO = _parse_prefijos(
    os.getenv("PREFIJOS_CARRO", "ABC,DEF,GHI,JKL,MNO,PQR,STU,XYZ")
)
PREFIJOS_MOTO = _parse_prefijos(
    os.getenv("PREFIJOS_MOTO", "AB,CD,EF,GH,JK,LM,NP,QR,ST,UV")
)

_rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)
_historial_consultas: list[dict[str, str]] = []

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

class Consulta(BaseModel):
    placa: str
    fecha: str
    hora: str
    resultado: str
    timestamp: str

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
    try:
        info_placa, fecha_obj, hora_obj, errores = validar_entrada(
            vehiculo.placa,
            vehiculo.fecha,
            vehiculo.hora
        )
        if errores:
            raise HTTPException(status_code=400, detail=errores)

        permitido = _puede_circular(
            info_placa["ultimo_digito"],
            fecha_obj,
            hora_obj
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    errores_prefijo = {}
    prefijos_config = (
        PREFIJOS_CARRO if info_placa["tipo"] == "carro" else PREFIJOS_MOTO
    )
    if prefijos_config and info_placa["prefijo"] not in prefijos_config:
        errores_prefijo["placa"] = (
            "Prefijo no reconocido para "
            f"{info_placa['tipo']}: {info_placa['prefijo']}"
        )
        raise HTTPException(status_code=400, detail=errores_prefijo)

    # Resultado texto
    resultado = (
        "Puede circular"
        if permitido
        else
        "No puede circular"
    )

    # Respuesta
    respuesta = {
        "placa": vehiculo.placa,
        "fecha": vehiculo.fecha,
        "hora": vehiculo.hora,
        "resultado": resultado
    }

    _historial_consultas.insert(0, {
        "placa": vehiculo.placa,
        "fecha": vehiculo.fecha,
        "hora": vehiculo.hora,
        "resultado": resultado,
        "timestamp": datetime.now().isoformat(timespec="seconds")
    })

    if len(_historial_consultas) > HISTORY_LIMIT:
        _historial_consultas.pop()

    return respuesta

@app.get("/historial", response_model=list[Consulta])
def obtener_historial(
    _: str = Depends(verificar_api_key),
    __: None = Depends(verificar_rate_limit)
):
    return _historial_consultas