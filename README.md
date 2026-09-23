# SilvaTwin — Backend Científico & API Geoespacial

Backend de servicios para el Gemelo Digital Forestal (**SilvaTwin**), desarrollado con **FastAPI**, **SQLAlchemy** y preparado para **PostgreSQL + PostGIS** mediante Docker Compose.

---

## 🏛 Arquitectura del Backend

```
Twin_Forestal_Backend/
├── docker-compose.yml       # Servicio PostgreSQL 16 con extensión PostGIS
├── requirements.txt         # Dependencias Python (FastAPI, SQLAlchemy, psycopg, etc.)
├── .env.example             # Plantilla de variables de entorno
├── .env                     # Variables de entorno activas
├── seed_data.py             # Script de población de datos iniciales en BD
├── test_api.py              # Suite de pruebas automatizadas
├── app/
│   ├── main.py              # Punto de entrada FastAPI con CORS y ciclo de vida
│   ├── core/
│   │   ├── config.py        # Configuración centralizada Pydantic Settings
│   │   └── database.py      # Motor de base de datos con fallback resiliente
│   ├── models/              # Modelos ORM (Region, Stand, FluxTimeSeries, Scenario)
│   ├── schemas/             # Validadores y esquemas Pydantic v2
│   ├── services/
│   │   ├── simulator.py     # Simulador numérico 3-PG ecofisiológico
│   │   └── ai_advisor.py    # Integración con Google Gemini AI + respaldo offline
│   └── api/
│       └── v1/
│           ├── router.py    # Enrutador principal de API v1
│           └── endpoints/   # Endpoints modulares (regions, stands, simulations, ai)
└── README.md
```

---

## 🚀 Puesta en Marcha Rápida

### 1. Levantar la Base de Datos con Docker (PostgreSQL + PostGIS)
Abre **Docker Desktop** en tu equipo y luego ejecuta en la terminal:

```bash
cd Twin_Forestal_Backend
docker compose up -d
```

Esto creará y dejará corriendo el contenedor `silvatwin_postgres` con PostGIS en el puerto `5432`.

> **Nota de Resiliencia:** Si aún no abres Docker, el backend cuenta con un fallback automático a SQLite local (`silvatwin.db`), permitiéndote probar la API inmediatamente sin bloqueos.

---

### 2. Configurar el Entorno Virtual de Python

En la terminal de Windows (PowerShell):

```bash
cd Twin_Forestal_Backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

### 3. Poblar la Base de Datos (Seed)

Ejecuta el script de siembra para inicializar las tablas y cargar las regiones, los rodales espaciales, las series temporales de flujo y los escenarios de manejo forestal:

```bash
python seed_data.py
```

---

### 4. Ejecutar Pruebas Automatizadas

Verifica que la base de datos y todos los endpoints funcionen correctamente:

```bash
python test_api.py
```

---

### 5. Iniciar el Servidor API

```bash
uvicorn app.main:app --reload --port 8000
```

* **API Base:** `http://localhost:8000`
* **Documentación Interactiva Swagger:** `http://localhost:8000/docs`
* **Documentación ReDoc:** `http://localhost:8000/redoc`
* **Health Check:** `http://localhost:8000/health`

---

## 📡 Endpoints Principales (API v1)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/health` | Estado del servicio y motor de BD activo |
| `GET` | `/api/v1/regions` | Lista de regiones paisajísticas forestales |
| `GET` | `/api/v1/regions/{id}` | Detalle de una región por ID |
| `GET` | `/api/v1/stands/region/{id}` | Rodales forestales con coordenadas y biomasa |
| `GET` | `/api/v1/simulations/flux-timeseries/{id}` | Series temporales mensuales FLUXNET / 3-PG / Deep Learning |
| `POST` | `/api/v1/simulations/3pg` | Ejecución del modelo numérico 3-PG con intervenciones |
| `GET` | `/api/v1/scenarios` | Escenarios a 50 años (clareos, quemas, restauración) |
| `POST` | `/api/v1/ai-advisor` | Asesor científico ecólogo (Gemini AI + contingencia) |
