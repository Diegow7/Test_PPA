import pytest

from pico_placa import validar_entrada, puede_circular


def test_validar_entrada_ok_carro():
    info, fecha_obj, hora_obj, errores = validar_entrada(
        "ABC1234",
        "2026-05-25",
        "08:00"
    )

    assert errores == {}
    assert info["tipo"] == "carro"
    assert info["ultimo_digito"] == 4
    assert fecha_obj.strftime("%Y-%m-%d") == "2026-05-25"
    assert hora_obj.strftime("%H:%M") == "08:00"


def test_validar_entrada_ok_moto():
    info, _, _, errores = validar_entrada(
        "AB123C",
        "2026-05-25",
        "09:15"
    )

    assert errores == {}
    assert info["tipo"] == "moto"
    assert info["ultimo_digito"] == 3


def test_validar_entrada_errores_por_campo():
    info, fecha_obj, hora_obj, errores = validar_entrada(
        "@@@",
        "",
        "25:99"
    )

    assert info is None
    assert fecha_obj is None
    assert hora_obj is None
    assert "placa" in errores
    assert "fecha" in errores
    assert "hora" in errores


def test_validar_entrada_fuera_rango_hora():
    _, _, _, errores = validar_entrada(
        "ABC1234",
        "2026-05-25",
        "20:00"
    )

    assert errores["hora"] == "Hora invalida: rango permitido 05:00 a 19:30"


def test_validar_entrada_hora_justo_antes_del_limite_inferior():
    _, _, _, errores = validar_entrada(
        "ABC1234",
        "2026-05-25",
        "04:59"
    )

    assert errores["hora"] == "Hora invalida: rango permitido 05:00 a 19:30"


def test_validar_entrada_hora_justo_despues_del_limite_superior():
    _, _, _, errores = validar_entrada(
        "ABC1234",
        "2026-05-25",
        "19:31"
    )

    assert errores["hora"] == "Hora invalida: rango permitido 05:00 a 19:30"


def test_validar_entrada_placa_vacia():
    info, _, _, errores = validar_entrada("", "2026-05-25", "08:00")

    assert info is None
    assert errores["placa"] == "Placa invalida: es obligatoria"


def test_validar_entrada_formato_hora_no_estricto():
    _, _, _, errores = validar_entrada(
        "ABC1234",
        "2026-05-25",
        "8:00"
    )

    assert errores["hora"] == "Hora invalida: formato esperado HH:MM"


def test_validar_entrada_placa_con_espacios_y_guiones():
    info, _, _, errores = validar_entrada(
        " ab-123 c ",
        "2026-05-25",
        "09:10"
    )

    assert errores == {}
    assert info["placa"] == "AB123C"
    assert info["tipo"] == "moto"


def test_validar_entrada_placa_con_separadores_consecutivos():
    _, _, _, errores = validar_entrada(
        "AB--123C",
        "2026-05-25",
        "09:10"
    )

    assert errores["placa"] == "Placa invalida: separadores consecutivos no permitidos"


def test_validar_entrada_fecha_y_hora_con_espacios():
    info, fecha_obj, hora_obj, errores = validar_entrada(
        "ABC1234",
        " 2026-05-25 ",
        " 08:00 "
    )

    assert errores == {}
    assert info["tipo"] == "carro"
    assert fecha_obj.strftime("%Y-%m-%d") == "2026-05-25"
    assert hora_obj.strftime("%H:%M") == "08:00"


def test_validar_entrada_fecha_con_barras():
    info, fecha_obj, _, errores = validar_entrada(
        "ABC1234",
        "2026/05/25",
        "08:00"
    )

    assert errores == {}
    assert info["tipo"] == "carro"
    assert fecha_obj.strftime("%Y-%m-%d") == "2026-05-25"


def test_validar_entrada_formato_fecha_no_estricto():
    _, _, _, errores = validar_entrada(
        "ABC1234",
        "2026-5-25",
        "08:00"
    )

    assert errores["fecha"] == "Fecha invalida: formato esperado YYYY-MM-DD"


def test_validar_entrada_placa_no_texto():
    info, _, _, errores = validar_entrada(
        None,
        "2026-05-25",
        "09:10"
    )

    assert info is None
    assert errores["placa"] == "Placa invalida: es obligatoria"


def test_validar_entrada_fecha_y_hora_no_texto():
    _, fecha_obj, hora_obj, errores = validar_entrada(
        "ABC1234",
        20260525,
        800
    )

    assert fecha_obj is None
    assert hora_obj is None
    assert errores["fecha"] == "Fecha invalida: debe ser texto"
    assert errores["hora"] == "Hora invalida: debe ser texto"


def test_puede_circular_restringido():
    assert puede_circular("ABC1231", "2026-05-25", "08:00") is False


def test_puede_circular_restringido_tarde():
    assert puede_circular("ABC1231", "2026-05-25", "16:30") is False


def test_puede_circular_permitido():
    assert puede_circular("ABC1230", "2026-05-25", "10:30") is True


def test_validar_entrada_hora_limite_inferior():
    _, _, hora_obj, errores = validar_entrada("ABC1234", "2026-05-25", "05:00")

    assert errores == {}
    assert hora_obj.strftime("%H:%M") == "05:00"


def test_validar_entrada_hora_limite_superior():
    _, _, hora_obj, errores = validar_entrada("ABC1234", "2026-05-25", "19:30")

    assert errores == {}
    assert hora_obj.strftime("%H:%M") == "19:30"


def test_puede_circular_lanza_value_error_si_entrada_invalida():
    import pytest
    with pytest.raises(ValueError, match="Placa invalida"):
        puede_circular("INVALID", "2026-05-25", "08:00")


def test_puede_circular_lanza_value_error_si_fecha_invalida():
    import pytest
    with pytest.raises(ValueError, match="Fecha invalida"):
        puede_circular("ABC1234", "not-a-date", "08:00")


def test_puede_circular_fin_de_semana():
    # 2026-08-08 es sábado — sin restricciones ningún dígito
    assert puede_circular("ABC1231", "2026-08-08", "08:00") is True
    assert puede_circular("ABC1239", "2026-08-09", "17:00") is True


def test_validar_entrada_fecha_futura():
    _, fecha_obj, _, errores = validar_entrada("ABC1234", "2099-01-01", "08:00")

    assert fecha_obj is None
    assert errores["fecha"] == "Fecha invalida: no puede ser futura"


def test_validar_entrada_fecha_imposible():
    _, fecha_obj, _, errores = validar_entrada("ABC1234", "2026-02-31", "08:00")

    assert fecha_obj is None
    assert "fecha" in errores


def test_restricciones_por_dia_de_semana():
    # Martes 2026-05-26: dígitos 3 y 4
    assert puede_circular("ABC1233", "2026-05-26", "08:00") is False
    assert puede_circular("ABC1234", "2026-05-26", "08:00") is False
    assert puede_circular("ABC1231", "2026-05-26", "08:00") is True
    # Miércoles 2026-05-27: dígitos 5 y 6
    assert puede_circular("ABC1235", "2026-05-27", "08:00") is False
    assert puede_circular("ABC1236", "2026-05-27", "08:00") is False
    # Jueves 2026-05-28: dígitos 7 y 8
    assert puede_circular("ABC1237", "2026-05-28", "08:00") is False
    assert puede_circular("ABC1238", "2026-05-28", "08:00") is False
    # Viernes 2026-05-29: dígitos 9 y 0
    assert puede_circular("ABC1239", "2026-05-29", "08:00") is False
    assert puede_circular("ABC1230", "2026-05-29", "08:00") is False


def test_placa_restringida_fuera_de_horario_puede_circular():
    # ABC1231 está restringida el lunes pero fuera de franja horaria puede circular
    assert puede_circular("ABC1231", "2026-05-25", "06:00") is True
    assert puede_circular("ABC1231", "2026-05-25", "10:00") is True
    assert puede_circular("ABC1231", "2026-05-25", "14:00") is True


def test_limites_exactos_franja_manana():
    # ABC1231 restringida el lunes — límites de franja mañana 07:00-09:30
    assert puede_circular("ABC1231", "2026-05-25", "07:00") is False
    assert puede_circular("ABC1231", "2026-05-25", "09:30") is False
    assert puede_circular("ABC1231", "2026-05-25", "06:59") is True


def test_limites_exactos_franja_tarde():
    # ABC1231 restringida el lunes — límites de franja tarde 16:00-19:30
    assert puede_circular("ABC1231", "2026-05-25", "16:00") is False
    assert puede_circular("ABC1231", "2026-05-25", "19:30") is False
    assert puede_circular("ABC1231", "2026-05-25", "15:59") is True


def test_validar_entrada_placa_longitud_invalida():
    _, _, _, errores = validar_entrada("AB12", "2026-05-25", "08:00")

    assert "placa" in errores
    assert "longitud" in errores["placa"].lower()


def test_validar_entrada_placa_solo_numeros():
    _, _, _, errores = validar_entrada("1234567", "2026-05-25", "08:00")

    assert "placa" in errores


def test_validar_entrada_placa_con_caracteres_especiales():
    _, _, _, errores = validar_entrada("ABC@1234", "2026-05-25", "08:00")

    assert "placa" in errores


def test_moto_extrae_digito_correcto():
    # Moto AB123C: el dígito restrictivo es el 3ro (2), no el último (C)
    # 2026-05-25 es lunes, restricción de dígitos 1 y 2
    info, _, _, errores = validar_entrada("AB123C", "2026-05-25", "08:00")

    assert errores == {}
    assert info["ultimo_digito"] == 2  # 3er digit position is the restriction
    assert info["tipo"] == "moto"


def test_extrae_prefijo_carro_y_moto():
    # Carro: prefijo son primeros 3 caracteres
    info_carro, _, _, _ = validar_entrada("ABC1234", "2026-05-25", "08:00")
    assert info_carro["prefijo"] == "ABC"
    assert info_carro["tipo"] == "carro"

    # Moto: prefijo son primeros 2 caracteres
    info_moto, _, _, _ = validar_entrada("XY123Z", "2026-05-25", "08:00")
    assert info_moto["prefijo"] == "XY"
    assert info_moto["tipo"] == "moto"


def test_validar_entrada_multiples_errores_simultaneos():
    # Placa inválida, fecha futura, hora fuera de rango - deben reportar todos los errores
    info, _, _, errores = validar_entrada("INVALID", "2099-12-31", "25:00")

    assert info is None
    assert "placa" in errores
    assert "fecha" in errores
    assert "hora" in errores
    assert len(errores) == 3
