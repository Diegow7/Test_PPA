from datetime import datetime
import re

FORMATO_FECHA = "%Y-%m-%d"
FORMATO_HORA = "%H:%M"
PATRON_HORA_ESTRICTA = re.compile(r"^\d{2}:\d{2}$")
PATRON_PLACA_CARRO = re.compile(r"^[A-Z]{3}[0-9]{4}$")
PATRON_PLACA_MOTO = re.compile(r"^[A-Z]{2}[0-9]{3}[A-Z]$")

# Restricciones por día
restricciones = {
    "Monday": [1, 2],
    "Tuesday": [3, 4],
    "Wednesday": [5, 6],
    "Thursday": [7, 8],
    "Friday": [9, 0]
}

HORA_INICIO_VALIDACION = datetime.strptime("05:00", FORMATO_HORA).time()
HORA_FIN_VALIDACION = datetime.strptime("19:30", FORMATO_HORA).time()
MANANA_INICIO = datetime.strptime("07:00", FORMATO_HORA).time()
MANANA_FIN = datetime.strptime("09:30", FORMATO_HORA).time()
TARDE_INICIO = datetime.strptime("16:00", FORMATO_HORA).time()
TARDE_FIN = datetime.strptime("19:30", FORMATO_HORA).time()

def _normalizar_texto_obligatorio(
    valor: object,
    mensaje_obligatorio: str,
    mensaje_tipo: str
) -> str:
    if not valor:
        raise ValueError(mensaje_obligatorio)

    if not isinstance(valor, str):
        raise ValueError(mensaje_tipo)

    valor = valor.strip()

    if not valor:
        raise ValueError(mensaje_obligatorio)

    return valor

def _validar_placa(placa: object) -> tuple[str, int, str, str]:

    if placa is None:
        raise ValueError("Placa invalida: es obligatoria")

    if not isinstance(placa, str):
        raise ValueError("Placa invalida: debe ser texto")

    # Normalizar la placa (por si viene con espacios o en minusculas)
    placa = placa.strip().upper()

    # Quitar separadores comunes y validar que solo tenga letras y numeros
    placa = re.sub(r"[-\s]", "", placa)
    if not placa:
        raise ValueError("Placa invalida: es obligatoria")

    if not placa.isalnum():
        raise ValueError("Placa invalida: solo letras y numeros")

    if len(placa) not in (6, 7):
        raise ValueError("Placa invalida: longitud esperada 6 (moto) o 7 (carro)")

    if PATRON_PLACA_CARRO.match(placa):
        ultimo_digito = int(placa[-1])
        prefijo = placa[:3]
        return placa, ultimo_digito, "carro", prefijo

    if PATRON_PLACA_MOTO.match(placa):
        ultimo_digito = int(placa[-2])
        prefijo = placa[:2]
        return placa, ultimo_digito, "moto", prefijo

    raise ValueError("Placa invalida: formato esperado AAA1111 o AA111A")

def obtener_info_placa(placa: object) -> dict[str, str | int]:
    placa_norm, ultimo_digito, tipo, prefijo = _validar_placa(placa)
    return {
        "placa": placa_norm,
        "ultimo_digito": ultimo_digito,
        "tipo": tipo,
        "prefijo": prefijo
    }

def _validar_fecha(fecha: object) -> datetime:
    fecha = _normalizar_texto_obligatorio(
        fecha,
        "Fecha invalida: es obligatoria",
        "Fecha invalida: debe ser texto"
    )
    fecha = fecha.replace("/", "-")

    try:
        fecha_obj = datetime.strptime(fecha, FORMATO_FECHA)
    except ValueError as exc:
        raise ValueError("Fecha invalida: formato esperado YYYY-MM-DD") from exc

    if fecha_obj.date() > datetime.now().date():
        raise ValueError("Fecha invalida: no puede ser futura")

    return fecha_obj

def _validar_hora(hora: object):
    hora = _normalizar_texto_obligatorio(
        hora,
        "Hora invalida: es obligatoria",
        "Hora invalida: debe ser texto"
    )

    if not PATRON_HORA_ESTRICTA.match(hora):
        raise ValueError("Hora invalida: formato esperado HH:MM")

    try:
        hora_obj = datetime.strptime(hora, FORMATO_HORA).time()
    except ValueError as exc:
        raise ValueError("Hora invalida: formato esperado HH:MM") from exc

    if not (HORA_INICIO_VALIDACION <= hora_obj <= HORA_FIN_VALIDACION):
        raise ValueError("Hora invalida: rango permitido 05:00 a 19:30")

    return hora_obj

def validar_entrada(placa: object, fecha: object, hora: object):
    errores = {}

    try:
        info = obtener_info_placa(placa)
    except ValueError as exc:
        errores["placa"] = str(exc)
        info = None

    try:
        fecha_obj = _validar_fecha(fecha)
    except ValueError as exc:
        errores["fecha"] = str(exc)
        fecha_obj = None

    try:
        hora_obj = _validar_hora(hora)
    except ValueError as exc:
        errores["hora"] = str(exc)
        hora_obj = None

    return info, fecha_obj, hora_obj, errores

def _esta_en_horario_restringido(hora_obj) -> bool:
    return (
        MANANA_INICIO <= hora_obj <= MANANA_FIN
        or
        TARDE_INICIO <= hora_obj <= TARDE_FIN
    )

def _puede_circular(ultimo_digito: int, fecha_obj: datetime, hora_obj) -> bool:
    # Obtener día de la semana
    dia_semana = fecha_obj.strftime("%A")

    digitos_restringidos = restricciones.get(dia_semana)
    if not digitos_restringidos:
        return True

    if ultimo_digito not in digitos_restringidos:
        return True

    return not _esta_en_horario_restringido(hora_obj)

def puede_circular(placa: object, fecha: object, hora: object) -> bool:
    info, fecha_obj, hora_obj, errores = validar_entrada(placa, fecha, hora)
    if errores:
        primer_error = next(iter(errores.values()))
        raise ValueError(primer_error)

    ultimo_digito = info["ultimo_digito"]

    return _puede_circular(ultimo_digito, fecha_obj, hora_obj)