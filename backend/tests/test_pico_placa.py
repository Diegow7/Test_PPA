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


def test_validar_entrada_placa_con_espacios_y_guiones():
    info, _, _, errores = validar_entrada(
        " ab-123 c ",
        "2026-05-25",
        "09:10"
    )

    assert errores == {}
    assert info["placa"] == "AB123C"
    assert info["tipo"] == "moto"


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


def test_validar_entrada_placa_no_texto():
    info, _, _, errores = validar_entrada(
        None,
        "2026-05-25",
        "09:10"
    )

    assert info is None
    assert errores["placa"] == "Placa invalida: es obligatoria"


def test_puede_circular_restringido():
    assert puede_circular("ABC1231", "2026-05-25", "08:00") is False


def test_puede_circular_restringido_tarde():
    assert puede_circular("ABC1231", "2026-05-25", "16:30") is False


def test_puede_circular_permitido():
    assert puede_circular("ABC1230", "2026-05-25", "10:30") is True
