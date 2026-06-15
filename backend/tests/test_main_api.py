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


def test_reglas_requiere_api_key():
    main.API_KEY = "test-key"
    response = client.get("/reglas")

    assert response.status_code == 401


def test_reglas_ok():
    response = client.get("/reglas", headers=_headers())

    assert response.status_code == 200
    data = response.json()
    assert "prefijos_carro" in data
    assert "prefijos_moto" in data
    assert "restricciones_por_dia" in data

    monday = next(item for item in data["restricciones_por_dia"] if item["dia"] == "Monday")
    assert monday["digitos"] == [1, 2]
