# Palmeras Records — Backend API

API RESTful desarrollada con **FastAPI** y **Python** para la gestión integral de catálogo discográfico, inventario por sedes físicas y procesamiento de archivos multimedia para Palmeras Records.

---

## 🛠️ Tecnologías

- **Lenguaje:** Python 3.10+
- **Framework:** FastAPI
- **Servidor ASGI:** Uvicorn
- **Base de Datos:** SQLite / SQLAlchemy
- **Almacenamiento Multimedia:** Cloudinary API
- **Cliente / Pruebas:** Swagger UI & ReDoc

---

## ⚙️ Puesta en marcha (Setup)

### 1. Clonar o acceder a la carpeta del backend
Desde la raíz del proyecto:
```bash
cd backend
```

### 2. Crear el entorno virtual
```bash
python -m venv .venv
```

### 3. Activar el entorno virtual

- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
- **Windows (CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```
- **Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
Crea un archivo `.env` en la raíz de `backend/` tomando como base la siguiente plantilla:

```env
# Application Settings
APP_TITLE="Palmeras en la Mancha Records API"
APP_VERSION="1.0.0"
APP_DESCRIPTION="REST API for managing record labels, albums and physical formats (Vinyl, CD, Cassette) for Palmeras en la Mancha Records, built with FastAPI, SQLAlchemy and SQLite."

# Database Settings
DATABASE_NAME="palmeras_records.sqlite3"
DATABASE_URL="sqlite:///./palmeras_records.sqlite3"

# Cloudinary Settings
CLOUDINARY_URL="cloudinary://<tu_api_key>:<tu_api_secret>@<tu_cloud_name>"
```
> **Nota:** Sustituye `<tu_api_key>`, `<tu_api_secret>` y `<tu_cloud_name>` por vuestras credenciales reales de Cloudinary.
```

### 6. Inicializar base de datos / Migraciones
```bash
alembic upgrade head
```
*(O ejecuta el script de inicialización de tablas si no usáis Alembic: `python database.py`)*

### 7. Iniciar el servidor de desarrollo
```bash
uvicorn main:app --reload
```

---

## 📖 Documentación Interactiva

Una vez iniciado el servidor, la API y su documentación interactiva estarán disponibles en:

- **Servidor base:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentación Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Documentación ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔗 Integración con el Frontend

Esta API da servicio a la aplicación web cliente construida con JavaScript modular y Axios.

- 📂 **Repositorio Frontend:** [Palmeras Records Frontend](https://github.com/TEAM-4-Palmeras-En-La-Mancha/Palmera_records_frontend)
- **CORS:** Por defecto, los endpoints admiten orígenes locales estándar (`http://localhost:5500`, `http://127.0.0.1:5500`, `http://localhost:3000`).
