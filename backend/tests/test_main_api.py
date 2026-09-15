from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def _headers():
    main.API_KEY = "test-key"
    return {"X-API-Key": "test-key"}


def test_healthcheck_ok():
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "historial_consultas" in data
    assert "uptime_seconds" in data
    assert "api_key_configurada" in data
    assert "rate_limit_max" in data
    assert "rate_limit_window_sec" in data
    assert "history_limit" in data
    assert data["rate_limit_max"] == main.RATE_LIMIT_MAX
    assert data["rate_limit_window_sec"] == main.RATE_LIMIT_WINDOW_SEC
    assert data["history_limit"] == main.HISTORY_LIMIT


def test_healthcheck_timestamp_iso_format():
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "T" in data["timestamp"]


def test_healthcheck_uptime_seconds_no_negativo():
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["uptime_seconds"], (int, float))
    assert data["uptime_seconds"] >= 0


def test_healthcheck_informa_consultas_guardadas():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    try:
        client.post("/validar", headers=headers, json={
            "placa": "ABC1230",
            "fecha": "2026-05-25",
            "hora": "10:30"
        })

        response = client.get("/health")

        assert response.status_code == 200
        assert response.json()["historial_consultas"] == 1
    finally:
        client.post("/historial/limpiar", headers=headers)


def test_healthcheck_informa_cero_consultas_con_historial_vacio():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["historial_consultas"] == 0


def test_healthcheck_informa_limite_del_historial():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["history_limit"] == main.HISTORY_LIMIT


def test_healthcheck_informa_ventana_del_rate_limit():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["rate_limit_window_sec"] == main.RATE_LIMIT_WINDOW_SEC


def test_healthcheck_informa_maximo_del_rate_limit():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["rate_limit_max"] == main.RATE_LIMIT_MAX


def test_healthcheck_devuelve_estado_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_healthcheck_sin_api_key():
    original_api_key = main.API_KEY
    main.API_KEY = ""

    try:
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["api_key_configurada"] is False
    finally:
        main.API_KEY = original_api_key


def test_healthcheck_con_api_key_configurada():
    original_api_key = main.API_KEY
    main.API_KEY = "test-key"

    try:
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["api_key_configurada"] is True
    finally:
        main.API_KEY = original_api_key


def test_healthcheck_no_requiere_api_key_con_api_configurada():
    original_api_key = main.API_KEY
    main.API_KEY = "test-key"

    try:
        response = client.get("/health")
        assert response.status_code == 200
    finally:
        main.API_KEY = original_api_key


def test_home_ok():
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Pico y Placa" in response.text


def test_reglas_requiere_api_key():
    main.API_KEY = "test-key"
    response = client.get("/reglas")

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_historial_requiere_api_key():
    main.API_KEY = "test-key"
    response = client.get("/historial")

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_limpiar_historial_requiere_api_key():
    main.API_KEY = "test-key"
    response = client.post("/historial/limpiar")

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_simular_requiere_api_key():
    main.API_KEY = "test-key"
    response = client.post("/simular", json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_validar_requiere_api_key():
    main.API_KEY = "test-key"
    response = client.post("/validar", json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_validar_acepta_api_key_con_espacios():
    main.API_KEY = "test-key"
    response = client.post("/validar", headers={"X-API-Key": "  test-key  "}, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200


def test_simular_rechaza_api_key_incorrecta():
    main.API_KEY = "test-key"
    response = client.post("/simular", headers={"X-API-Key": "wrong-key"}, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_validar_rechaza_api_key_incorrecta():
    main.API_KEY = "test-key"
    response = client.post("/validar", headers={"X-API-Key": "wrong-key"}, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_simular_acepta_api_key_con_espacios():
    main.API_KEY = "test-key"
    response = client.post("/simular", headers={"X-API-Key": "  test-key  "}, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200


def test_historial_rechaza_api_key_incorrecta():
    main.API_KEY = "test-key"
    response = client.get("/historial", headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_historial_acepta_api_key_con_espacios():
    main.API_KEY = "test-key"
    response = client.get("/historial", headers={"X-API-Key": "  test-key  "})

    assert response.status_code == 200


def test_limpiar_historial_rechaza_api_key_incorrecta():
    main.API_KEY = "test-key"
    response = client.post("/historial/limpiar", headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_limpiar_historial_acepta_api_key_con_espacios():
    main.API_KEY = "test-key"
    response = client.post("/historial/limpiar", headers={"X-API-Key": "  test-key  "})

    assert response.status_code == 200


def test_reglas_rechaza_api_key_incorrecta():
    main.API_KEY = "test-key"
    response = client.get("/reglas", headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401
    assert response.json()["detail"] == "API key invalida"


def test_reglas_ok():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    data = response.json()
    assert "prefijos_carro" in data
    assert "prefijos_moto" in data
    assert data["horario_validacion"] == "05:00-19:30"
    assert data["franjas_restringidas"] == ["07:00-09:30", "16:00-19:30"]
    assert "restricciones_por_dia" in data

    monday = next(item for item in data["restricciones_por_dia"] if item["dia"] == "Monday")
    assert monday["digitos"] == [1, 2]


def test_reglas_devuelve_prefijos_carro_configurados():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    assert response.json()["prefijos_carro"] == main.PREFIJOS_CARRO


def test_reglas_devuelve_prefijos_moto_configurados():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    assert response.json()["prefijos_moto"] == main.PREFIJOS_MOTO


def test_reglas_incluye_cinco_dias_laborales():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    data = response.json()
    assert len(data["restricciones_por_dia"]) == 5


def test_reglas_viernes_digitos_correctos():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    data = response.json()
    friday = next(item for item in data["restricciones_por_dia"] if item["dia"] == "Friday")
    assert friday["digitos"] == [9, 0]


def test_reglas_martes_digitos_correctos():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    data = response.json()
    tuesday = next(item for item in data["restricciones_por_dia"] if item["dia"] == "Tuesday")
    assert tuesday["digitos"] == [3, 4]


def test_reglas_miercoles_digitos_correctos():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    data = response.json()
    wednesday = next(item for item in data["restricciones_por_dia"] if item["dia"] == "Wednesday")
    assert wednesday["digitos"] == [5, 6]


def test_reglas_jueves_digitos_correctos():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    data = response.json()
    thursday = next(item for item in data["restricciones_por_dia"] if item["dia"] == "Thursday")
    assert thursday["digitos"] == [7, 8]


def test_reglas_incluye_dias_laborales_esperados():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    data = response.json()
    dias = {item["dia"] for item in data["restricciones_por_dia"]}
    assert dias == {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday"}


def test_reglas_acepta_api_key_con_espacios():
    main.API_KEY = "test-key"
    response = client.get("/reglas", headers={"X-API-Key": "  test-key  "})

    assert response.status_code == 200


def test_simular_ok():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "Puede circular"
    assert data["simulado"] is True


def test_simular_no_puede_circular():
    # ABC1231 termina en 1, restringido el lunes 2026-05-25 en horario de mañana
    response = client.post("/simular", headers=_headers(), json={
        "placa": "ABC1231",
        "fecha": "2026-05-25",
        "hora": "08:00"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "No puede circular"
    assert data["simulado"] is True


def test_simular_restringida_fuera_de_franja_horaria():
    # ABC1231 está restringida lunes, pero fuera de franja debe poder circular
    response = client.post("/simular", headers=_headers(), json={
        "placa": "ABC1231",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "Puede circular"
    assert data["simulado"] is True


def test_simular_no_incluye_timestamp():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    data = response.json()
    assert "timestamp" not in data


def test_simular_respuesta_incluye_campos_esperados():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {"placa", "fecha", "hora", "resultado", "simulado"}


def test_validar_no_incluye_simulado():
    # /validar no debe incluir el campo simulado; solo /simular lo retorna
    response = client.post("/validar", headers=_headers(), json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "Puede circular"
    assert "simulado" not in data


def test_validar_datos_invalidos_devuelve_400():
    response = client.post("/validar", headers=_headers(), json={
        "placa": "INVALID",
        "fecha": "not-a-date",
        "hora": "99:99"
    })

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert set(detail) == {"placa", "fecha", "hora"}


def test_procesar_consulta_conserva_datos_validos():
    vehiculo = main.Vehiculo(
        placa="ABC1230",
        fecha="2026-05-25",
        hora="10:30"
    )

    respuesta = main._procesar_consulta(vehiculo)

    assert respuesta == {
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30",
        "resultado": "Puede circular"
    }


def test_procesar_consulta_restringida_devuelve_no_puede_circular():
    vehiculo = main.Vehiculo(
        placa="ABC1231",
        fecha="2026-05-25",
        hora="08:00"
    )

    respuesta = main._procesar_consulta(vehiculo)

    assert respuesta["resultado"] == "No puede circular"


def test_procesar_consulta_acepta_hora_limite_superior():
    vehiculo = main.Vehiculo(
        placa="ABC1230",
        fecha="2026-05-25",
        hora="19:30"
    )

    respuesta = main._procesar_consulta(vehiculo)

    assert respuesta["resultado"] == "Puede circular"


def test_procesar_consulta_acepta_hora_limite_inferior():
    vehiculo = main.Vehiculo(
        placa="ABC1230",
        fecha="2026-05-25",
        hora="05:00"
    )

    respuesta = main._procesar_consulta(vehiculo)

    assert respuesta["resultado"] == "Puede circular"


def test_procesar_consulta_rechaza_hora_fuera_de_rango():
    import pytest

    vehiculo = main.Vehiculo(
        placa="ABC1230",
        fecha="2026-05-25",
        hora="04:59"
    )

    with pytest.raises(main.HTTPException) as error:
        main._procesar_consulta(vehiculo)

    assert error.value.status_code == 400
    assert error.value.detail["hora"] == "Hora invalida: rango permitido 05:00 a 19:30"


def test_procesar_consulta_rechaza_fecha_futura():
    import pytest

    vehiculo = main.Vehiculo(
        placa="ABC1230",
        fecha="2099-01-01",
        hora="10:30"
    )

    with pytest.raises(main.HTTPException) as error:
        main._procesar_consulta(vehiculo)

    assert error.value.status_code == 400
    assert error.value.detail["fecha"] == "Fecha invalida: no puede ser futura"


def test_procesar_consulta_rechaza_fecha_imposible():
    import pytest

    vehiculo = main.Vehiculo(
        placa="ABC1230",
        fecha="2026-02-31",
        hora="10:30"
    )

    with pytest.raises(main.HTTPException) as error:
        main._procesar_consulta(vehiculo)

    assert error.value.status_code == 400
    assert error.value.detail["fecha"] == "Fecha invalida: formato esperado YYYY-MM-DD"


def test_procesar_consulta_rechaza_prefijo_no_configurado():
    import pytest

    vehiculo = main.Vehiculo(
        placa="ZZZ1234",
        fecha="2026-05-25",
        hora="10:30"
    )

    with pytest.raises(main.HTTPException) as error:
        main._procesar_consulta(vehiculo)

    assert error.value.status_code == 400
    assert error.value.detail["placa"] == "Prefijo no reconocido para carro: ZZZ"


def test_validar_rechaza_prefijo_no_configurado():
    response = client.post("/validar", headers=_headers(), json={
        "placa": "ZZZ1234",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 400
    assert response.json()["detail"]["placa"] == "Prefijo no reconocido para carro: ZZZ"


def test_validar_rechaza_prefijo_moto_no_configurado():
    response = client.post("/validar", headers=_headers(), json={
        "placa": "ZZ123Z",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 400
    assert response.json()["detail"]["placa"] == "Prefijo no reconocido para moto: ZZ"


def test_validar_acepta_moto_con_prefijo_configurado():
    response = client.post("/validar", headers=_headers(), json={
        "placa": "AB123C",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    assert response.json()["resultado"] == "Puede circular"


def test_validar_normaliza_prefijo_carro_en_minusculas():
    response = client.post("/validar", headers=_headers(), json={
        "placa": "abc1234",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    assert response.json()["resultado"] == "Puede circular"


def test_validar_normaliza_prefijo_moto_en_minusculas():
    response = client.post("/validar", headers=_headers(), json={
        "placa": "ab123c",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    assert response.json()["resultado"] == "Puede circular"


def test_validar_acepta_placa_con_espacios_y_guiones():
    response = client.post("/validar", headers=_headers(), json={
        "placa": " abc-1234 ",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    assert response.json()["resultado"] == "Puede circular"


def test_simular_datos_invalidos_devuelve_400():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "INVALID",
        "fecha": "not-a-date",
        "hora": "99:99"
    })

    assert response.status_code == 400


def test_simular_error_no_guarda_en_historial():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    response = client.post("/simular", headers=headers, json={
        "placa": "ZZZ1234",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    historial = client.get("/historial", headers=headers)

    assert response.status_code == 400
    assert historial.status_code == 200
    assert historial.json() == []


def test_simular_rechaza_prefijo_no_configurado():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "ZZZ1234",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 400
    assert response.json()["detail"]["placa"] == "Prefijo no reconocido para carro: ZZZ"


def test_simular_normaliza_prefijo_carro_en_minusculas():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "abc1234",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "Puede circular"
    assert data["simulado"] is True


def test_simular_normaliza_prefijo_moto_en_minusculas():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "ab123c",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "Puede circular"
    assert data["simulado"] is True


def test_simular_acepta_placa_con_espacios_y_guiones():
    response = client.post("/simular", headers=_headers(), json={
        "placa": " abc-1234 ",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "Puede circular"
    assert data["simulado"] is True


def test_simular_rechaza_prefijo_moto_no_configurado():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "ZZ123Z",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 400
    assert response.json()["detail"]["placa"] == "Prefijo no reconocido para moto: ZZ"


def test_simular_acepta_moto_con_prefijo_configurado():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "AB123C",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "Puede circular"
    assert data["simulado"] is True


def test_simular_moto_restringida_no_puede_circular():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "AB123C",
        "fecha": "2026-05-25",
        "hora": "08:00"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "No puede circular"
    assert data["simulado"] is True


def test_validar_no_puede_circular():
    # ABC1231 termina en 1, restringido el lunes 2026-05-25 en horario de mañana
    response = client.post("/validar", headers=_headers(), json={
        "placa": "ABC1231",
        "fecha": "2026-05-25",
        "hora": "08:00"
    })

    assert response.status_code == 200
    assert response.json()["resultado"] == "No puede circular"


def test_validar_moto_restringida_no_puede_circular():
    response = client.post("/validar", headers=_headers(), json={
        "placa": "AB123C",
        "fecha": "2026-05-25",
        "hora": "08:00"
    })

    assert response.status_code == 200
    assert response.json()["resultado"] == "No puede circular"


def test_validar_restringida_fuera_de_franja_horaria():
    # ABC1231 está restringida lunes, pero solo en horas de restricción (07:00-09:30)
    # A las 10:30 del lunes puede circular aunque esté restringida ese día
    response = client.post("/validar", headers=_headers(), json={
        "placa": "ABC1231",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    assert response.status_code == 200
    assert response.json()["resultado"] == "Puede circular"


def test_validar_fin_de_semana_puede_circular():
    # ABC1231 estaría restringida lunes, pero en sábado debe poder circular
    response = client.post("/validar", headers=_headers(), json={
        "placa": "ABC1231",
        "fecha": "2026-05-23",
        "hora": "08:00"
    })

    assert response.status_code == 200
    assert response.json()["resultado"] == "Puede circular"


def test_simular_fin_de_semana_puede_circular():
    response = client.post("/simular", headers=_headers(), json={
        "placa": "ABC1231",
        "fecha": "2026-05-23",
        "hora": "08:00"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["resultado"] == "Puede circular"
    assert data["simulado"] is True


def test_validar_puede_circular():
    # ABC1230 termina en 0, restringido viernes; este es viernes pero hora de mediodía (fuera de rango)
    response = client.post("/validar", headers=_headers(), json={
        "placa": "ABC1230",
        "fecha": "2026-05-22",
        "hora": "12:00"
    })

    assert response.status_code == 200
    assert response.json()["resultado"] == "Puede circular"


def test_validar_guarda_en_historial():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    client.post("/validar", headers=headers, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    response = client.get("/historial", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["placa"] == "ABC1230"


def test_validar_error_no_guarda_en_historial():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    response = client.post("/validar", headers=headers, json={
        "placa": "ZZZ1234",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    historial = client.get("/historial", headers=headers)

    assert response.status_code == 400
    assert historial.status_code == 200
    assert historial.json() == []


def test_historial_orden_mas_reciente_primero():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    client.post("/validar", headers=headers, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })
    client.post("/validar", headers=headers, json={
        "placa": "ABC1232",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    response = client.get("/historial", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["placa"] == "ABC1232"
    assert data[1]["placa"] == "ABC1230"


def test_historial_incluye_timestamp_en_cada_entrada():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    client.post("/validar", headers=headers, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    response = client.get("/historial", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "timestamp" in data[0]
    assert data[0]["timestamp"]


def test_historial_campos_completos_en_cada_registro():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    client.post("/validar", headers=headers, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    response = client.get("/historial", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert set(data[0].keys()) == {"placa", "fecha", "hora", "resultado", "timestamp"}


def test_simular_no_guarda_en_historial():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    client.post("/simular", headers=headers, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    response = client.get("/historial", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 0


def test_historial_respeta_history_limit():
    headers = _headers()
    original_limit = main.HISTORY_LIMIT
    main.HISTORY_LIMIT = 2
    client.post("/historial/limpiar", headers=headers)

    try:
        client.post("/validar", headers=headers, json={
            "placa": "ABC1230",
            "fecha": "2026-05-25",
            "hora": "10:30"
        })
        client.post("/validar", headers=headers, json={
            "placa": "ABC1231",
            "fecha": "2026-05-25",
            "hora": "10:30"
        })
        client.post("/validar", headers=headers, json={
            "placa": "ABC1232",
            "fecha": "2026-05-25",
            "hora": "10:30"
        })

        response = client.get("/historial", headers=headers)

        assert response.status_code == 200
        assert len(response.json()) == 2
    finally:
        main.HISTORY_LIMIT = original_limit
        client.post("/historial/limpiar", headers=headers)


def test_limpiar_historial_ok():
    headers = _headers()

    client.post("/historial/limpiar", headers=headers)

    client.post("/validar", headers=headers, json={
        "placa": "ABC1230",
        "fecha": "2026-05-25",
        "hora": "10:30"
    })

    response = client.post("/historial/limpiar", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["historial_vacio"] is True
    assert data["eliminadas"] >= 1
    assert data["restantes"] == 0


def test_limpiar_historial_ya_vacio():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    response = client.post("/historial/limpiar", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["historial_vacio"] is True
    assert data["eliminadas"] == 0
    assert data["restantes"] == 0


def test_historial_vacio_devuelve_array_vacio():
    headers = _headers()
    client.post("/historial/limpiar", headers=headers)

    response = client.get("/historial", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


def test_rate_limit_bloqueado():
    headers = _headers()
    original_max = main.RATE_LIMIT_MAX

    main.RATE_LIMIT_MAX = 2
    main._rate_limit_buckets.clear()

    try:
        for _ in range(2):
            client.get("/health")

        response = client.get("/health")
        assert response.status_code == 429
        assert response.json()["detail"] == "Demasiadas solicitudes, intenta mas tarde"
    finally:
        main.RATE_LIMIT_MAX = original_max
        main._rate_limit_buckets.clear()
