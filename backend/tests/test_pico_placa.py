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


def test_puede_circular_fin_de_semana():
    # 2026-08-08 es sábado — sin restricciones ningún dígito
    assert puede_circular("ABC1231", "2026-08-08", "08:00") is True
    assert puede_circular("ABC1239", "2026-08-09", "17:00") is True
