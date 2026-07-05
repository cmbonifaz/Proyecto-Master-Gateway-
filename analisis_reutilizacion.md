# 📊 Análisis de Reutilización — Proyecto Parcial III (Desarrollo Seguro 2026-50)

---

## 🗂️ Inventario de Archivos del Proyecto Existente

| Archivo | Propósito actual |
|---|---|
| `.github/workflows/pipeline-seguro.yml` | Pipeline CI/CD con 3 Jobs (ML Gatekeeper, Pytest, Deploy) |
| `backend/Dockerfile` | Docker seguro con usuario no-root |
| `backend/requirements.txt` | FastAPI, Pydantic, pytest, bleach |
| `backend/app/main.py` | Entry point FastAPI (LiveSeat API) |
| `backend/app/api/router.py` | Router modular de FastAPI |
| `backend/app/api/endpoints/eventos.py` | Endpoints GET/POST de Eventos |
| `backend/app/api/endpoints/reservas.py` | Endpoints GET/POST de Reservas |
| `backend/app/schemas/event.py` | Schema Pydantic con sanitización XSS (bleach) |
| `backend/app/schemas/reservation.py` | Schema Pydantic con EmailStr, regex, límites |
| `backend/app/models/domain.py` | Modelos de dominio internos |
| `backend/app/db/repository.py` | Repositorio en memoria (BD simulada) |
| `backend/app/services/event_service.py` | Servicio de lógica de negocio (Eventos) |
| `backend/app/services/reservation_service.py` | Servicio de lógica de negocio (Reservas) |
| `backend/tests/test_main.py` | 4 pruebas pytest (positivas + negativas de seguridad) |
| `scripts/analizador_ci.py` | Gatekeeper ML (785 líneas): AST + TF-IDF + RF |
| `scripts/generar_diff.py` | Utilidad para generar diffs simulados |
| `pipeline/models/*.joblib` | Modelo Random Forest ya entrenado (96.4% accuracy) |
| `pipeline/requirements.txt` | Deps ML: sklearn, pandas, numpy, joblib |
| `pipeline/fase1_ingesta_feature_engineering.py` | Script completo de entrenamiento del modelo |

---

## ✅ Lo que se puede reutilizar DIRECTAMENTE (sin o con poco cambio)

### 🏆 Reutilización completa (100%)

| Componente | Por qué reutilizar |
|---|---|
| **`scripts/analizador_ci.py`** | Es el corazón del SAST con ML. Detecta 6 categorías de vulnerabilidades (SQLi, Command Injection, Deserialización, Path Traversal, Secrets, XSS/SSRF). Funciona sobre cualquier PR de código Python. **No tiene dependencia del dominio de negocio**. |
| **`pipeline/models/*.joblib`** | El modelo Random Forest ya entrenado (96.4% accuracy en CVEFixes dataset) se puede usar directamente en el pipeline del nuevo proyecto. |
| **`pipeline/requirements.txt`** | Dependencias ML son las mismas. |
| **`scripts/generar_diff.py`** | Utilidad de apoyo genérica para testing local. |

### 🔧 Reutilizable con adaptaciones

| Componente | Qué adaptar |
|---|---|
| **`.github/workflows/pipeline-seguro.yml`** | El esqueleto de los 3 Jobs (ML Gatekeeper → Pytest → Deploy) es **idéntico** a lo que pide el PDF. Solo hay que: (1) ajustar el trigger, (2) agregar el paso de **SonarCloud** (que el PDF exige y el proyecto actual no tiene), (3) cambiar el nombre del servicio en Render. |
| **`backend/Dockerfile`** | Perfectamente reutilizable. Solo cambiar el entrypoint si el módulo principal tiene distinto nombre. |
| **`backend/requirements.txt`** | Se amplía con: `python-jose[cryptography]` (JWT), `passlib[bcrypt]` (hashing), `sqlalchemy` (ORM con PostgreSQL), `alembic` (migraciones). |
| **`backend/app/main.py`** | La estructura de `FastAPI + include_router` es idéntica. Solo cambiar `title` y agregar los nuevos routers. |
| **`backend/app/api/router.py`** | Mismo patrón modular de routers. Se reemplaza `eventos/reservas` por `auth/users/roles/modules/menus`. |
| **`backend/app/schemas/*.py`** | El **patrón de validación con Pydantic + bleach** es exactamente lo que pide el PDF (Shift-Left). Se reutiliza el patrón para los schemas de User, Role, Module, Menu. |
| **`backend/tests/test_main.py`** | Los 4 tests de seguridad (injection, XSS, límites) son el **modelo exacto** de lo que hay que hacer para los nuevos endpoints. Se replica el patrón de negative testing. |
| **`backend/app/services/*.py`** | El patrón de Clean Architecture (endpoint → service → repository) es el mismo. Se replican para auth, users, roles, etc. |

---

## ❌ Lo que NO se puede reutilizar (dominio específico)

| Componente | Por qué no |
|---|---|
| `backend/app/models/domain.py` | Modelos `EventoDomain` / `ReservaDomain` — son del negocio LiveSeat. Se reemplazan por `User`, `Role`, `Module`, `Menu`. |
| `backend/app/db/repository.py` | BD en memoria (dict). El nuevo proyecto requiere **PostgreSQL o MySQL con ORM real** (SQLAlchemy/Prisma). |
| `backend/app/api/endpoints/eventos.py` y `reservas.py` | Endpoints de negocio LiveSeat. Se reemplazan completamente. |

---

## 🗺️ Mapa de Reutilización para el Nuevo Proyecto

```
PROYECTO ACTUAL              NUEVO PROYECTO (P-III)
────────────────────         ──────────────────────────────────
analizador_ci.py    ───────► Reutilizar IGUAL (SAST ML)
pipeline/models/    ───────► Reutilizar IGUAL (modelo entrenado)
Dockerfile          ───────► Reutilizar con pequeños ajustes
workflow YAML       ───────► Adaptar + agregar SonarCloud step
main.py (estructura)───────► Reutilizar patrón FastAPI
router.py (patrón)  ───────► Mismo patrón, nuevos routers
schemas (patrón)    ───────► Replicar para User/Role/Menu schemas
tests (patrón)      ───────► Replicar negative testing para auth
                             ↓
                       NUEVO a construir:
                       - ORM (SQLAlchemy + PostgreSQL)
                       - JWT doble token (TempToken + JWT final)
                       - Workspace Selector endpoint
                       - Menús recursivos con CTE
                       - CRUD Users / Roles / Modules / Menus
                       - Soft Delete + auditoría ORM
                       - SonarCloud en el pipeline
```

---

## 📋 Resumen Ejecutivo

El proyecto existente **ahorra construir desde cero** la parte más compleja:
el **pipeline ML/SAST y el Gatekeeper**, que es el componente más valioso
y diferenciador del nuevo proyecto.

La arquitectura de backend (FastAPI + Clean Architecture + Pydantic) también
es **totalmente transferible**.

### Lo que hay que construir nuevo:
- El **dominio de negocio**: auth JWT de doble paso, CRUD de users/roles/menus
  con ORM real y PostgreSQL.
- Los **campos de auditoría** obligatorios por entidad (`estado`, `fecha_creacion`,
  `fecha_actualizacion`, `creado_por`, `actualizado_por`) manejados por el ORM.
- **Soft Delete** global a nivel de ORM (nunca DELETE físico).
- **Menús recursivos** con CTE (`WITH RECURSIVE`) para evitar el problema N+1.
- **Workspace Selector** (pantalla de selección de rol entre login y dashboard).
- **SonarCloud** integrado como paso adicional en el pipeline CI/CD.
- **Endpoint interno** `POST /api/internals/validate-token` para microservicios hijos.
