from datetime import datetime

# Restricciones por día
restricciones = {
    "Monday": [1, 2],
    "Tuesday": [3, 4],
    "Wednesday": [5, 6],
    "Thursday": [7, 8],
    "Friday": [9, 0]
}

def puede_circular(placa, fecha, hora):

    # Obtener último número de la placa
    ultimo_digito = int(placa[-1])

    # Convertir fecha
    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")

    # Obtener día de la semana
    dia_semana = fecha_obj.strftime("%A")

    # Convertir hora
    hora_obj = datetime.strptime(hora, "%H:%M").time()

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