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

def _validar_placa(placa):

    # Normalizar la placa (por si viene con espacios o en minusculas)
    placa = placa.strip().upper()

    # Quitar guiones y validar que solo tenga letras y numeros
    placa = placa.replace("-", "")
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
    if not fecha:
        raise ValueError("Fecha invalida: es obligatoria")

    try:
        return datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Fecha invalida: formato esperado YYYY-MM-DD") from exc

def _validar_hora(hora):
    if not hora:
        raise ValueError("Hora invalida: es obligatoria")

    try:
        hora_obj = datetime.strptime(hora, "%H:%M").time()
    except ValueError as exc:
        raise ValueError("Hora invalida: formato esperado HH:MM") from exc

    hora_inicio = datetime.strptime("05:00", "%H:%M").time()
    hora_fin = datetime.strptime("12:00", "%H:%M").time()
    if not (hora_inicio <= hora_obj <= hora_fin):
        raise ValueError("Hora invalida: rango permitido 05:00 a 12:00")

    return hora_obj

def puede_circular(placa, fecha, hora):
    info = obtener_info_placa(placa)
    ultimo_digito = info["ultimo_digito"]

    # Convertir fecha
    fecha_obj = _validar_fecha(fecha)

    # Obtener día de la semana
    dia_semana = fecha_obj.strftime("%A")

    # Convertir hora
    hora_obj = _validar_hora(hora)

    # Horarios restringidos
    manana_inicio = datetime.strptime("07:00", "%H:%M").time()
    manana_fin = datetime.strptime("09:30", "%H:%M").time()

    tarde_inicio = datetime.strptime("16:00", "%H:%M").time()
    tarde_fin = datetime.strptime("19:30", "%H:%M").time()

    # Verificar si está en horario restringido
    en_horario_restringido = (
        manana_inicio <= hora_obj <= manana_fin
        or
        tarde_inicio <= hora_obj <= tarde_fin
    )

    # Verificar restricción del día
    if dia_semana in restricciones:

        if ultimo_digito in restricciones[dia_semana]:

            if en_horario_restringido:
                return False

    return True