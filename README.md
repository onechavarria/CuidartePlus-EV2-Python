# CuidartePlus - EV2 DevOps

Backend con dos microservicios en Python (FastAPI), PostgreSQL y Docker Compose. No incluye frontend.

## Requisitos

- Docker Desktop
- Python 3.13 para ejecutar pruebas localmente

## Ejecutar con Docker

Desde la carpeta principal:

```bash
docker compose up -d --build
docker compose ps
```

Abrir Swagger:

- Usuarios: http://localhost:4444/docs
- Pacientes: http://localhost:4445/docs

Para detener:

```bash
docker compose down
```

Para reiniciar la base de datos desde cero, **se pierden los datos**:

```bash
docker compose down -v
docker compose up -d --build
```

## Pruebas y cobertura

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt

python -m pip install -r usuarios/requirements.txt
python -m pip install -r pacientes/requirements.txt

python -m pytest --version
python -m pytest -v --cov=usuarios/app --cov=pacientes/app --cov-branch --cov-report=html --cov-report=term-missing --cov-fail-under=80

start htmlcov/index.html
```

Abrir `htmlcov/index.html` para ver el reporte.

## GitHub Actions y SonarCloud

El workflow `.github/workflows/ci-cd.yml` se ejecuta al hacer push a `main`. Ejecuta pruebas, cobertura, SonarCloud y despliegue temporal con Docker Compose.

En `sonar-project.properties` reemplaza `REEMPLAZAR_PROJECT_KEY` y `REEMPLAZAR_ORGANIZATION_KEY` con los valores de tu proyecto SonarCloud. En GitHub crea el secreto `SONAR_TOKEN` en Settings > Secrets and variables > Actions. El token nunca debe ponerse en archivos del repositorio.

Dependabot revisa las dependencias cada semana.

## Variables

El archivo `.env` incluye únicamente credenciales de ejemplo para ejecutar localmente. Puedes subirlo a GitHub para este laboratorio, pero **cambia las claves y utiliza secretos fuera del repositorio si publicas el proyecto**.

