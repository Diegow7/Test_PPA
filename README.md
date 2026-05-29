# Proyecto Pico y Placa

Sistema desarrollado con FastAPI y PostgreSQL para validar si un vehículo puede circular según las reglas de Pico y Placa.

## Tecnologías usadas

- Python
- FastAPI
- PostgreSQL
- HTML
- CSS
- JavaScript

## Funcionalidades

- Validar circulación vehicular
- Guardar historial de consultas
- API REST
- Frontend simple

## Ejecutar proyecto

### Instalar dependencias

```CMD commands for execute
cd backend
venv\Scripts\activate
pip install -r requirements.txt
python -m pip install -r requirements.txt
uvicorn main:app --reload  
```

### Ejecutar pruebas

```CMD commands for execute
cd backend
venv\Scripts\activate
pytest
```