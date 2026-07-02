from datetime import datetime
import re

# Restricciones por día
restricciones = {
    "Monday": [1, 2],
    "Tuesday": [3, 4],
    "Wednesday": [5, 6],
    "Thursday": [7, 8],
    "Friday": [9, 0]
}

HORA_INICIO_VALIDACION = datetime.strptime("05:00", "%H:%M").time()
HORA_FIN_VALIDACION = datetime.strptime("19:30", "%H:%M").time()
MANANA_INICIO = datetime.strptime("07:00", "%H:%M").time()
MANANA_FIN = datetime.strptime("09:30", "%H:%M").time()
TARDE_INICIO = datetime.strptime("16:00", "%H:%M").time()
TARDE_FIN = datetime.strptime("19:30", "%H:%M").time()

def _normalizar_texto_obligatorio(valor, mensaje_error):
    if not valor:
        raise ValueError(mensaje_error)

    if not isinstance(valor, str):
        raise ValueError(mensaje_error.replace("es obligatoria", "debe ser texto").replace("es obligatorio", "debe ser texto"))

    valor = valor.strip()

    if not valor:
        raise ValueError(mensaje_error)

    return valor

def _validar_placa(placa):

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

    patron_carro = r"^[A-Z]{3}[0-9]{4}$"
    patron_moto = r"^[A-Z]{2}[0-9]{3}[A-Z]$"

    if re.match(patron_carro, placa):
        ultimo_digito = int(placa[-1])
        prefijo = placa[:3]
        return placa, ultimo_digito, "carro", prefijo

    if re.match(patron_moto, placa):
        ultimo_digito = int(placa[-2])
        prefijo = placa[:2]
        return placa, ultimo_digito, "moto", prefijo

    raise ValueError("Placa invalida: formato esperado AAA1111 o AA111A")

def obtener_info_placa(placa):
    placa_norm, ultimo_digito, tipo, prefijo = _validar_placa(placa)
    return {
        "placa": placa_norm,
        "ultimo_digito": ultimo_digito,
        "tipo": tipo,
        "prefijo": prefijo
    }

def _validar_fecha(fecha):
    fecha = _normalizar_texto_obligatorio(fecha, "Fecha invalida: es obligatoria")
    fecha = fecha.replace("/", "-")

    try:
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Fecha invalida: formato esperado YYYY-MM-DD") from exc

    if fecha_obj.date() > datetime.now().date():
        raise ValueError("Fecha invalida: no puede ser futura")

    return fecha_obj

def _validar_hora(hora):
    hora = _normalizar_texto_obligatorio(hora, "Hora invalida: es obligatoria")

    try:
        hora_obj = datetime.strptime(hora, "%H:%M").time()
    except ValueError as exc:
        raise ValueError("Hora invalida: formato esperado HH:MM") from exc

    if not (HORA_INICIO_VALIDACION <= hora_obj <= HORA_FIN_VALIDACION):
        raise ValueError("Hora invalida: rango permitido 05:00 a 19:30")

    return hora_obj

def validar_entrada(placa, fecha, hora):
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

def _puede_circular(ultimo_digito, fecha_obj, hora_obj):
    # Obtener día de la semana
    dia_semana = fecha_obj.strftime("%A")

    # Verificar si está en horario restringido
    en_horario_restringido = (
        MANANA_INICIO <= hora_obj <= MANANA_FIN
        or
        TARDE_INICIO <= hora_obj <= TARDE_FIN
    )

    # Verificar restricción del día
    if dia_semana in restricciones:

        if ultimo_digito in restricciones[dia_semana]:

            if en_horario_restringido:
                return False

    return True

def puede_circular(placa, fecha, hora):
    info, fecha_obj, hora_obj, errores = validar_entrada(placa, fecha, hora)
    if errores:
        primer_error = next(iter(errores.values()))
        raise ValueError(primer_error)

    ultimo_digito = info["ultimo_digito"]

    return _puede_circular(ultimo_digito, fecha_obj, hora_obj)