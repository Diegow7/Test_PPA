from datetime import datetime, time
import re
from types import MappingProxyType

FORMATO_FECHA = "%Y-%m-%d"
FORMATO_HORA = "%H:%M"
PATRON_FECHA_ESTRICTA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PATRON_HORA_ESTRICTA = re.compile(r"^\d{2}:\d{2}$")
PATRON_PLACA_CARRO = re.compile(r"^[A-Z]{3}[0-9]{4}$")
PATRON_PLACA_MOTO = re.compile(r"^[A-Z]{2}[0-9]{3}[A-Z]$")
PATRON_SEPARADORES_PLACA = re.compile(r"[-\s]")
PATRON_SEPARADORES_CONSECUTIVOS = re.compile(r"[-\s]{2,}")

# Restricciones por día
restricciones = MappingProxyType({
    "Monday": [1, 2],
    "Tuesday": [3, 4],
    "Wednesday": [5, 6],
    "Thursday": [7, 8],
    "Friday": [9, 0]
})

HORA_INICIO_VALIDACION = datetime.strptime("05:00", FORMATO_HORA).time()
HORA_FIN_VALIDACION = datetime.strptime("19:30", FORMATO_HORA).time()
MANANA_INICIO = datetime.strptime("07:00", FORMATO_HORA).time()
MANANA_FIN = datetime.strptime("09:30", FORMATO_HORA).time()
TARDE_INICIO = datetime.strptime("16:00", FORMATO_HORA).time()
TARDE_FIN = datetime.strptime("19:30", FORMATO_HORA).time()
FRANJAS_RESTRINGIDAS = (
    (MANANA_INICIO, MANANA_FIN),
    (TARDE_INICIO, TARDE_FIN)
)

def _normalizar_texto_obligatorio(
    valor: object,
    mensaje_obligatorio: str,
    mensaje_tipo: str
) -> str:
    """
    Normaliza y valida que un texto requerido sea válido.
    
    Args:
        valor: El valor a normalizar.
        mensaje_obligatorio: Mensaje de error si el valor es vacío.
        mensaje_tipo: Mensaje de error si el valor no es texto.
    
    Returns:
        El texto normalizado (sin espacios al inicio/final).
    
    Raises:
        ValueError: Si el valor es vacío, no es texto, o es solo espacios.
    """
    if not valor:
        raise ValueError(mensaje_obligatorio)

    if not isinstance(valor, str):
        raise ValueError(mensaje_tipo)

    valor = valor.strip()

    if not valor:
        raise ValueError(mensaje_obligatorio)

    return valor

def _validar_placa(placa: object) -> tuple[str, int, str, str]:
    """
    Valida el formato de una placa vehicular ecuatoriana.
    
    Acepta dos formatos:
    - Carro: AAA1111 (3 letras, 4 dígitos)
    - Moto: AA111A (2 letras, 3 dígitos, 1 letra)
    
    Args:
        placa: La placa a validar (puede incluir separadores como '-' o espacios).
    
    Returns:
        Tupla con (placa_normalizada, último_dígito, tipo, prefijo).
    
    Raises:
        ValueError: Si la placa no cumple con el formato requerido.
    """

    if placa is None:
        raise ValueError("Placa invalida: es obligatoria")

    if not isinstance(placa, str):
        raise ValueError("Placa invalida: debe ser texto")

    # Normalizar la placa (por si viene con espacios o en minusculas)
    placa = placa.strip().upper()

    if PATRON_SEPARADORES_CONSECUTIVOS.search(placa):
        raise ValueError("Placa invalida: separadores consecutivos no permitidos")

    # Quitar separadores comunes y validar que solo tenga letras y numeros
    placa = PATRON_SEPARADORES_PLACA.sub("", placa)
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
    """
    Extrae información detallada de una placa vehicular válida.
    
    Args:
        placa: La placa a procesar.
    
    Returns:
        Diccionario con claves: placa, último_dígito, tipo, prefijo.
    
    Raises:
        ValueError: Si la placa es inválida.
    """
    placa_norm, ultimo_digito, tipo, prefijo = _validar_placa(placa)
    return {
        "placa": placa_norm,
        "ultimo_digito": ultimo_digito,
        "tipo": tipo,
        "prefijo": prefijo
    }

def _validar_fecha(fecha: object) -> datetime:
    """
    Valida que una fecha esté en formato YYYY-MM-DD y no sea futura.
    
    Args:
        fecha: La fecha a validar (texto en formato YYYY-MM-DD).
    
    Returns:
        Objeto datetime con la fecha validada.
    
    Raises:
        ValueError: Si la fecha es inválida, tiene formato incorrecto o es futura.
    """
    fecha = _normalizar_texto_obligatorio(
        fecha,
        "Fecha invalida: es obligatoria",
        "Fecha invalida: debe ser texto"
    )
    fecha = fecha.replace("/", "-")

    if not PATRON_FECHA_ESTRICTA.match(fecha):
        raise ValueError("Fecha invalida: formato esperado YYYY-MM-DD")

    try:
        fecha_obj = datetime.strptime(fecha, FORMATO_FECHA)
    except ValueError as exc:
        raise ValueError("Fecha invalida: formato esperado YYYY-MM-DD") from exc

    if fecha_obj.date() > datetime.now().date():
        raise ValueError("Fecha invalida: no puede ser futura")

    return fecha_obj

def _validar_hora(hora: object) -> time:
    """
    Valida que una hora esté en formato HH:MM y dentro del rango permitido.
    
    Rango válido: 05:00 a 19:30.
    
    Args:
        hora: La hora a validar (texto en formato HH:MM).
    
    Returns:
        Objeto time con la hora validada.
    
    Raises:
        ValueError: Si la hora es inválida, tiene formato incorrecto o fuera de rango.
    """
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

def validar_entrada(
    placa: object,
    fecha: object,
    hora: object
) -> tuple[dict[str, str | int] | None, datetime | None, time | None, dict[str, str]]:
    """
    Valida todos los parámetros de entrada (placa, fecha, hora).
    
    Realiza validación de cada campo independientemente y retorna los resultados.
    
    Args:
        placa: Placa vehicular a validar.
        fecha: Fecha en formato YYYY-MM-DD.
        hora: Hora en formato HH:MM.
    
    Returns:
        Tupla con (info_placa, fecha_obj, hora_obj, errores_dict).
        - Los objetos pueden ser None si hay error.
        - errores_dict contiene claves: 'placa', 'fecha', 'hora'.
    """
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

def _esta_en_horario_restringido(hora_obj: time) -> bool:
    """
    Verifica si una hora cae dentro de los horarios restringidos.
    
    Horarios restringidos:
    - Mañana: 07:00 - 09:30
    - Tarde: 16:00 - 19:30
    
    Args:
        hora_obj: Objeto time a verificar.
    
    Returns:
        True si la hora está dentro de un horario restringido, False en caso contrario.
    """
    return any(inicio <= hora_obj <= fin for inicio, fin in FRANJAS_RESTRINGIDAS)

def _puede_circular(ultimo_digito: int, fecha_obj: datetime, hora_obj: time) -> bool:
    """
    Determina si un vehículo puede circular según su último dígito, fecha y hora.
    
    Implementa la lógica de Pico y Placa:
    - Lunes-Martes: Dígitos 1, 2
    - Miércoles-Jueves: Dígitos 5, 6
    - Viernes: Dígitos 9, 0
    
    Un vehículo NO puede circular si:
    - Su dígito coincide con la restricción del día
    - Y la hora está dentro de un horario restringido
    
    Args:
        ultimo_digito: Último dígito de la placa (0-9).
        fecha_obj: Objeto datetime de la consulta.
        hora_obj: Objeto time de la consulta.
    
    Returns:
        True si el vehículo puede circular, False si está restringido.
    """
    # Obtener día de la semana
    dia_semana = fecha_obj.strftime("%A")

    digitos_restringidos = restricciones.get(dia_semana)
    if not digitos_restringidos:
        return True

    if ultimo_digito not in digitos_restringidos:
        return True

    return not _esta_en_horario_restringido(hora_obj)

def puede_circular(placa: object, fecha: object, hora: object) -> bool:
    """
    Valida si un vehículo puede circular en una fecha y hora específicas.
    
    Realiza validación completa de entrada y aplica las reglas de Pico y Placa.
    
    Args:
        placa: Placa vehicular (formato: AAA1111 o AA111A).
        fecha: Fecha de consulta (formato: YYYY-MM-DD).
        hora: Hora de consulta (formato: HH:MM).
    
    Returns:
        True si el vehículo puede circular, False si está restringido.
    
    Raises:
        ValueError: Si algún parámetro es inválido.
    """
    info, fecha_obj, hora_obj, errores = validar_entrada(placa, fecha, hora)
    if errores:
        primer_error = next(iter(errores.values()))
        raise ValueError(primer_error)

    ultimo_digito = info["ultimo_digito"]

    return _puede_circular(ultimo_digito, fecha_obj, hora_obj)