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

from pico_placa import (
    HORA_FIN_VALIDACION,
    HORA_INICIO_VALIDACION,
    MANANA_FIN,
    MANANA_INICIO,
    TARDE_FIN,
    TARDE_INICIO,
    restricciones,
    validar_entrada,
    _puede_circular,
)

# Crear app
app = FastAPI()
APP_START_TIME = time.time()

API_KEY = (os.getenv("API_KEY") or "").strip()
RATE_LIMIT_MAX = int(os.getenv("RATE_LIMIT_MAX", "30"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "60"))
HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "20"))
CORS_ORIGINS = [
    origen.strip()
    for origen in os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",")
    if origen.strip()
]

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
    allow_origins=CORS_ORIGINS,
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

class ReglaDia(BaseModel):
    dia: str
    digitos: list[int]

class ReglasPicoPlaca(BaseModel):
    prefijos_carro: list[str]
    prefijos_moto: list[str]
    horario_validacion: str
    franjas_restringidas: list[str]
    restricciones_por_dia: list[ReglaDia]

def verificar_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key no configurada")

    api_key_header = (x_api_key or "").strip()

    if api_key_header != API_KEY:
        raise HTTPException(status_code=401, detail="API key invalida")

    return api_key_header

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

def _procesar_consulta(vehiculo: Vehiculo) -> dict:
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

    resultado = (
        "Puede circular"
        if permitido
        else
        "No puede circular"
    )

    return {
        "placa": vehiculo.placa,
        "fecha": vehiculo.fecha,
        "hora": vehiculo.hora,
        "resultado": resultado
    }

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
    respuesta = _procesar_consulta(vehiculo)

    _historial_consultas.insert(0, {
        "placa": vehiculo.placa,
        "fecha": vehiculo.fecha,
        "hora": vehiculo.hora,
        "resultado": respuesta["resultado"],
        "timestamp": datetime.now().isoformat(timespec="seconds")
    })

    if len(_historial_consultas) > HISTORY_LIMIT:
        _historial_consultas.pop()

    return respuesta

@app.post("/simular")
def simular_vehiculo(
    vehiculo: Vehiculo,
    _: str = Depends(verificar_api_key),
    __: None = Depends(verificar_rate_limit)
):
    respuesta = _procesar_consulta(vehiculo)
    respuesta["simulado"] = True
    return respuesta

@app.get("/health")
def healthcheck():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "historial_consultas": len(_historial_consultas),
        "uptime_seconds": round(time.time() - APP_START_TIME, 2),
        "api_key_configurada": bool(API_KEY)
    }

@app.get("/reglas", response_model=ReglasPicoPlaca)
def obtener_reglas(
    _: str = Depends(verificar_api_key),
    __: None = Depends(verificar_rate_limit)
):
    return {
        "prefijos_carro": PREFIJOS_CARRO,
        "prefijos_moto": PREFIJOS_MOTO,
        "horario_validacion": (
            f"{HORA_INICIO_VALIDACION.strftime('%H:%M')}-"
            f"{HORA_FIN_VALIDACION.strftime('%H:%M')}"
        ),
        "franjas_restringidas": [
            f"{MANANA_INICIO.strftime('%H:%M')}-{MANANA_FIN.strftime('%H:%M')}",
            f"{TARDE_INICIO.strftime('%H:%M')}-{TARDE_FIN.strftime('%H:%M')}"
        ],
        "restricciones_por_dia": [
            {"dia": dia, "digitos": digitos}
            for dia, digitos in restricciones.items()
        ]
    }

@app.get("/historial", response_model=list[Consulta])
def obtener_historial(
    _: str = Depends(verificar_api_key),
    __: None = Depends(verificar_rate_limit)
):
    return _historial_consultas

@app.post("/historial/limpiar")
def limpiar_historial(
    _: str = Depends(verificar_api_key),
    __: None = Depends(verificar_rate_limit)
):
    cantidad = len(_historial_consultas)
    _historial_consultas.clear()
    return {
        "historial_vacio": True,
        "eliminadas": cantidad,
        "restantes": len(_historial_consultas)
    }