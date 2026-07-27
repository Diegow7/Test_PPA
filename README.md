# Proyecto Pico y Placa

Sistema desarrollado con FastAPI y frontend web (HTML, CSS y JavaScript) para validar si un vehículo puede circular según las reglas de Pico y Placa en Ecuador.

**Pico y Placa:** Restricción vehicular diaria basada en el último dígito de la placa, prohibiendo la circulación en ciertos horarios.

## Requisitos previos

- Python 3.8+
- pip o pip3

## Tecnologías usadas

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML5, CSS3, JavaScript (ES6+)
- **Testing:** pytest, httpx

## Estructura del proyecto

```
Test_PPA/
├── backend/
│   ├── main.py          # Aplicación FastAPI
│   ├── pico_placa.py    # Lógica de validación
│   ├── requirements.txt  # Dependencias Python
│   ├── .env.example     # Plantilla de configuración
│   └── tests/           # Pruebas unitarias
├── frontend/
│   ├── index.html       # Interfaz web
│   ├── app.js           # Lógica del cliente
│   └── style.css        # Estilos
└── README.md
```

## Instalación y configuración

### 1. Crear entorno virtual

```bash
python -m venv venv
```

### 2. Activar entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
cd backend
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

Editar `.env` con tus valores:

```
API_KEY=tu-clave-secreta
CORS_ORIGINS=http://localhost:8000
```

## Ejecutar proyecto

```bash
cd backend
uvicorn main:app --reload
```

Acceder a: `http://localhost:8000`

## Ejecutar pruebas

```bash
cd backend
pytest
```

Con cobertura:

```bash
pytest --cov=. --cov-report=html
```

## Endpoints disponibles

- `POST /validar` - Validar circulación
- `POST /simular` - Simular sin guardar
- `GET /health` - Estado de la aplicación
- `GET /reglas` - Reglas de restricción
- `GET /historial` - Historial de consultas
- `POST /historial/limpiar` - Limpiar historial