# 🛡️ Microservicio Master de Autenticación y Autorización — Pipeline DevSecOps

<div align="center">

![Pipeline Status](https://img.shields.io/badge/Pipeline-Activo-brightgreen?style=for-the-badge&logo=github-actions)
![ML Accuracy](https://img.shields.io/badge/ML%20Accuracy-96.4%25-blue?style=for-the-badge&logo=scikit-learn)
![Python](https://img.shields.io/badge/Python-3.11-yellow?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?style=for-the-badge&logo=postgresql)
![SonarQube](https://img.shields.io/badge/SonarQube-Community-4E9BCD?style=for-the-badge&logo=sonarqube)
![Docker](https://img.shields.io/badge/Docker-Seguro-2496ED?style=for-the-badge&logo=docker)
![Render](https://img.shields.io/badge/Render-Producción-46E3B7?style=for-the-badge&logo=render)

**🌐 API en Producción:** [https://pipeline-seguro.onrender.com](https://pipeline-seguro.onrender.com)  
**📖 Documentación Swagger:** [https://pipeline-seguro.onrender.com/docs](https://pipeline-seguro.onrender.com/docs)

</div>

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Flujo de Trabajo (Branches)](#-flujo-de-trabajo-branches)
- [Pipeline CI/CD — 4 Jobs](#-pipeline-cicd--4-jobs)
- [Job 1 — Gatekeeper ML](#job-1--gatekeeper-de-seguridad-ml)
- [Job 2 — SonarQube Community](#job-2--análisis-sast-sonarqube-community)
- [Job 3 — Pytest](#job-3--merge-automático-y-pytest)
- [Job 4 — Deploy Render](#job-4--despliegue-a-producción)
- [El Modelo de Machine Learning](#-el-modelo-de-machine-learning)
- [API — Endpoints Disponibles](#-api--endpoints-disponibles)
- [Seguridad Implementada](#-seguridad-implementada)
- [GitHub Secrets Requeridos](#-github-secrets-requeridos)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Setup Local](#-setup-local)

---

## 🌟 Descripción General

Este proyecto implementa un **Microservicio Master de Autenticación y Autorización** con un pipeline CI/CD DevSecOps completamente automatizado. Combina **Machine Learning clásico** (Random Forest) con **SonarQube Community** para detectar vulnerabilidades antes de que el código llegue a producción.

### Principio Shift-Left Security

La seguridad ocurre **antes** del merge, no después del despliegue:

```
Código en PR → ML Gatekeeper → SonarQube Quality Gate → Pytest → Deploy
                   ↑                    ↑
          Bloquea vulnerable    Bloquea deuda técnica
          (96.4% accuracy)      (reglas OWASP/CWE)
```

### Características Principales

| Característica | Detalle |
|---|---|
| **Auth** | JWT de doble paso — TempToken → JWT definitivo por rol |
| **SAST ML** | Random Forest + TF-IDF + 7 features AST (CVEFixes dataset) |
| **SAST Estático** | SonarQube Community self-hosted (sin exponer a internet) |
| **ORM** | SQLAlchemy async + Alembic + PostgreSQL (Supabase) |
| **Auditoría** | Soft Delete global + campos `estado`, `fecha_creacion`, `creado_por` en todos los modelos |
| **Notificaciones** | Bot de Telegram en tiempo real (cada etapa del pipeline) |
| **Despliegue** | Docker en Render, merge automático `test → main` |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DEVELOPER (rama dev / feature/*)                        │
│                        Commit + Pull Request → test                         │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   GITHUB ACTIONS: pipeline-seguro.yml                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │  JOB 1           │  runs-on: ubuntu-latest                              │
│  │  Gatekeeper ML   │──── VULNERABLE? ──▶ Bloquear PR + Issue + Telegram 🚨│
│  │  (RF + AST)      │──── SEGURO?    ──┐                                   │
│  └──────────────────┘                  │                                   │
│                                        ▼                                   │
│  ┌──────────────────┐                                                       │
│  │  JOB 2           │  runs-on: self-hosted (tu PC, accede a localhost)    │
│  │  SonarQube SAST  │──── GATE FAIL? ──▶ Notificar Telegram ❌             │
│  │  Quality Gate    │──── GATE PASS? ──┐                                   │
│  └──────────────────┘                  │                                   │
│                                        ▼                                   │
│  ┌──────────────────┐                                                       │
│  │  JOB 3           │  runs-on: ubuntu-latest                              │
│  │  Merge + Pytest  │──── FAIL? ──▶ Label 'tests-failed' + Telegram ❌    │
│  │  (rama test)     │──── PASS? ──┐                                        │
│  └──────────────────┘             │                                        │
│                                   ▼                                        │
│  ┌──────────────────┐                                                       │
│  │  JOB 4           │  runs-on: ubuntu-latest                              │
│  │  Deploy Render   │──── PR test→main (auto) + Webhook Render            │
│  │  (rama main)     │──── Notificación final a Telegram 🎉                │
│  └──────────────────┘                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│           RENDER — pipeline-seguro.onrender.com                             │
│           FastAPI + PostgreSQL (Supabase) en Docker (usuario no-root)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌿 Flujo de Trabajo (Branches)

```
  feature/* ──PR──▶  dev  ──PR──▶  test  ──PR auto──▶  main
                      │              │                    │
               Desarrollo       Staging QA          Producción
                                    │
                        Pipeline se dispara aquí
                        (PR dev → test)
```

| Rama | Propósito |
|---|---|
| `feature/*` | Funcionalidades individuales, se mergean a `dev` |
| `dev` | Desarrollo activo. Origen de los Pull Requests al pipeline |
| `test` | Staging. Código que pasó ML + SonarQube + Pytest |
| `main` | Producción. Solo código verificado por el pipeline completo |

> **Ramas protegidas:** `main` y `test` tienen Branch Protection Rules configuradas — no se permite push directo, solo merge vía PR aprobado por el pipeline.

---

## 🔄 Pipeline CI/CD — 4 Jobs

### JOB 1 — Gatekeeper de Seguridad ML

**Entorno:** `runs-on: ubuntu-latest` (servidores de GitHub)

```yaml
gatekeeper-security-check:
  steps:
    - Checkout del código
    - Notificar inicio de revisión vía Telegram ⏳
    - Setup Python 3.11
    - Instalar scikit-learn==1.8.0 + joblib (versión exacta del modelo)
    - Extraer diff del PR (gh pr diff)
    - Ejecutar scripts/analizador_ci.py con el diff
    - VULNERABLE → Comentar PR + Cerrar PR + Issue + Telegram 🚨
    - SEGURO    → Notificar éxito vía Telegram ✅
```

**Motor de decisión en 3 capas:**

| Capa | Mecanismo | Bloquea solo |
|---|---|---|
| **Capa 1** | Random Forest (96.4% accuracy) | Si pred=1 O prob ≥ 50% |
| **Capa 2** | AST determinista (`pickle.loads`, `os.system`, `hashlib.md5`, etc.) | Siempre que detecta |
| **Capa 3** | Heurísticas de texto (SQLi, XSS keywords) | Solo añade detalle al reporte |

---

### JOB 2 — Análisis SAST SonarQube Community

**Entorno:** `runs-on: self-hosted` ← tu PC local donde corre SonarQube

```yaml
sonarqube-analysis:
  needs: gatekeeper-security-check
  runs-on: self-hosted          # El runner accede a http://localhost:9000 directamente
  steps:
    - Checkout del código (con fetch-depth: 0 para blame)
    - Notificar inicio vía Telegram 🔍
    - Ejecutar SonarQube Scanner (sonarsource/sonarqube-scan-action)
      - sonar.projectKey=pipeline-seguro
      - sonar.sources=backend/app
      - sonar.tests=backend/tests
      - sonar.python.version=3.11
    - Verificar Quality Gate (sonarsource/sonarqube-quality-gate-action)
    - FAIL → Notificar Telegram ❌
    - PASS → Notificar Telegram ✅
```

**Variables usadas del Secret:**
- `SONAR_TOKEN` — Token de usuario generado en SonarQube
- `SONAR_HOST_URL` — `http://localhost:9000` (accesible solo desde tu runner local)

> **¿Por qué self-hosted?** El servidor SonarQube corre en tu red local. Al usar un self-hosted runner instalado en tu PC, el agente puede contactar `http://localhost:9000` directamente sin necesitar Ngrok ni exponer puertos a internet.

---

### JOB 3 — Merge Automático y Pytest

**Entorno:** `runs-on: ubuntu-latest`

```yaml
auto-merge-and-test:
  needs: [gatekeeper-security-check, sonarqube-analysis]
  steps:
    - Setup Python 3.11
    - Instalar backend/requirements.txt
    - Ejecutar pytest backend/tests/ -v
      (Con SQLite en memoria — no requiere conexión a Supabase)
    - FAIL → Label 'tests-failed' + Telegram ❌
    - PASS → gh pr merge --admin + Telegram ✅
```

**Tests cubiertos:**

| Archivo | Qué prueba |
|---|---|
| `test_auth.py` | Login doble paso, TempToken → JWT, mensaje genérico en fallo |
| `test_users.py` | Validación contraseña fuerte (Shift-Left), sanitización XSS |
| `test_roles.py` | Validación regex nombre rol, prevención eliminar ADMIN |
| `test_menus.py` | Árbol recursivo de menús vía CTE, ciclos en parent_id |

---

### JOB 4 — Despliegue a Producción

**Entorno:** `runs-on: ubuntu-latest`

```yaml
deploy-production:
  needs: auto-merge-and-test
  steps:
    - Checkout rama 'test'
    - Crear PR automático test → main
    - gh pr merge --admin (merge automático)
    - curl webhook Render (trigger redeploy Docker)
    - Notificación final a Telegram 🎉
```

---

## 🤖 El Modelo de Machine Learning

> **Restricción cumplida:** No se usan LLMs. Todo el análisis es **ML clásico** entrenado localmente sobre CVEFixes.

### Dataset y Algoritmo

| Componente | Detalle |
|---|---|
| **Dataset** | CVEFixes — vulnerabilidades reales de repositorios Git |
| **Vectorizador** | TF-IDF (Term Frequency–Inverse Document Frequency) |
| **Clasificador** | `RandomForestClassifier(random_state=42)` |
| **Accuracy** | **96.43%** — Validación cruzada estratificada 10-fold |
| **Datos sintéticos** | +1,200 muestras (Juliet Test Suite NSA/NIST) |

### 7 Features AST Extraídas

| Feature | Descripción | Categoría |
|---|---|---|
| `ast_depth` | Profundidad máxima del árbol AST | General |
| `dangerous_func_count` | Llamadas a `eval`, `exec`, `os.system`, `subprocess.Popen` | Cat. 2–6 |
| `total_calls` | Total de llamadas a funciones | General |
| `num_imports` | Número de sentencias `import` | General |
| `has_string_concat` | Concatenación de strings (riesgo SQLi/XSS) | Cat. 1, 6 |
| `num_exception_handlers` | Bloques `except` (supresión de errores) | General |
| `has_hardcoded_secret` | Credencial con valor literal en el código | Cat. 5 |

### Categorías de Vulnerabilidades Detectadas

| Cat. | Tipo | Método |
|---|---|---|
| 1 | SQL Injection | AST + Heurística |
| 2 | Command Injection (`eval`, `exec`, `os.system`) | AST + Heurística |
| 3 | Deserialización Insegura (`pickle.loads`, `yaml.load`) | AST + Heurística |
| 4 | Path Traversal (`open(concat)`, `open(f-string)`) | AST especializado |
| 5 | Secretos Hardcodeados + Criptografía Débil (`md5`, `sha1`) | AST + Heurística |
| 6 | XSS (concat HTML) + SSRF (URL dinámica) | AST + Heurística |

---

## 🔌 API — Endpoints Disponibles

### Auth (`/api/auth/`)

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/auth/login` | Credenciales → TempToken + lista de roles |
| `POST` | `/api/auth/select-role` | TempToken + roleId → JWT definitivo |
| `POST` | `/api/auth/refresh-token` | Renueva JWT. Revoca si hay reutilización |
| `POST` | `/api/auth/logout` | Invalida tokens activos |

### Internals (`/api/internals/`)

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/internals/validate-token` | Endpoint Zero Trust para microservicios hijos |

### Gestión (`/api/users/`, `/api/roles/`, `/api/modules/`, `/api/menus/`)

| Recurso | Operaciones |
|---|---|
| **Users** | CRUD completo + asignación de roles |
| **Roles** | CRUD + prevención de eliminar ADMIN |
| **Modules** | CRUD |
| **Menus** | CRUD + `GET /api/menus/tree` (árbol recursivo CTE) |

> Todos los DELETE son **Soft Delete** (`estado = 'INACTIVO'`). Nunca DELETE físico.

---

## 🔒 Seguridad Implementada

| Requisito | Implementación |
|---|---|
| Hash de contraseñas | `passlib[bcrypt]` con cost factor alto |
| JWT Zero Trust | `python-jose[cryptography]`, expiración corta, doble paso |
| Consultas seguras | Solo ORM SQLAlchemy — sin string interpolation |
| Secrets | `pydantic-settings` + GitHub Secrets → Render env vars |
| Login genérico | HTTP 401 sin especificar qué falló (usuario vs contraseña) |
| Ocultar password | Serialización ORM excluye `password_hash` del response |
| Validación input | Pydantic: regex, tipos, longitudes máx, `EmailStr`, `bleach` |
| Auditoría ORM | `BaseAudit`: `estado`, `fecha_creacion`, `fecha_actualizacion`, `creado_por`, `actualizado_por` |

### Variables de Entorno (Render)

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db   # Supabase
JWT_SECRET=<secreto_fuerte_min_32_chars>
JWT_ALGORITHM=HS256
TEMP_TOKEN_EXPIRE_MINUTES=5
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 🔑 GitHub Secrets Requeridos

| Secret | Descripción | Cómo obtenerlo |
|---|---|---|
| `TELEGRAM_TOKEN` | Token del bot de Telegram | [@BotFather](https://t.me/BotFather) → `/newbot` |
| `TELEGRAM_CHAT_ID` | ID del grupo/chat | [@userinfobot](https://t.me/userinfobot) |
| `RENDER_DEPLOY_HOOK_URL` | Webhook de redeploy | Render Dashboard → Settings → Deploy Hook |
| `SONAR_TOKEN` | Token de usuario SonarQube | SonarQube → My Account → Security → Tokens |
| `SONAR_HOST_URL` | URL del servidor SonarQube | `http://localhost:9000` (accedido por runner local) |
| `GITHUB_TOKEN` | Gestión de PRs e Issues | Automático en GitHub Actions |

> **Configuración adicional en GitHub:**  
> Settings → Actions → General → Workflow permissions:  
> ✅ Read and write permissions  
> ✅ Allow GitHub Actions to create and approve pull requests

> **Self-hosted runner:**  
> Settings → Actions → Runners → New self-hosted runner → seguir los pasos para Windows.  
> El runner se registra en tu PC y ejecuta el Job de SonarQube localmente, accediendo a `http://localhost:9000` sin necesitar Ngrok ni exponer puertos.

---

## 📁 Estructura del Repositorio

```
pipeline-seguro/
│
├── .github/
│   └── workflows/
│       └── pipeline-seguro.yml     ← Pipeline CI/CD (4 Jobs DevSecOps)
│
├── backend/
│   ├── Dockerfile                  ← Imagen Docker segura (non-root, python:3.11-slim)
│   ├── requirements.txt            ← Dependencias FastAPI + JWT + SQLAlchemy + pytest
│   ├── alembic.ini                 ← Configuración Alembic
│   ├── alembic/
│   │   └── versions/               ← Migraciones de base de datos
│   ├── app/
│   │   ├── main.py                 ← Entry point FastAPI
│   │   ├── core/
│   │   │   ├── config.py           ← Variables de entorno (pydantic-settings)
│   │   │   ├── database.py         ← Engine async SQLAlchemy + SessionLocal
│   │   │   ├── security.py         ← JWT encode/decode, bcrypt hash
│   │   │   └── dependencies.py     ← get_db, get_current_user (Depends)
│   │   ├── models/
│   │   │   ├── base.py             ← BaseAudit (soft delete + auditoría global)
│   │   │   ├── user.py, role.py, module.py, menu.py
│   │   │   └── user_role.py, role_module.py, role_menu.py
│   │   ├── schemas/
│   │   │   └── auth.py, user.py, role.py, module.py, menu.py
│   │   ├── services/
│   │   │   └── auth_service.py, user_service.py, role_service.py, ...
│   │   └── api/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── auth.py         ← /api/auth/*
│   │           ├── internals.py    ← /api/internals/validate-token
│   │           ├── users.py, roles.py, modules.py, menus.py
│   │           └── db/
│   │               └── seed.py     ← Datos iniciales (admin, roles base)
│   └── tests/
│       ├── conftest.py             ← BD SQLite en memoria + cliente HTTP async
│       ├── test_auth.py
│       ├── test_users.py
│       ├── test_roles.py
│       └── test_menus.py
│
├── scripts/
│   ├── analizador_ci.py            ← Gatekeeper ML (Random Forest + AST, 3 capas)
│   └── generar_diff.py             ← Utilidad de testing local
│
├── pipeline/
│   ├── fase1_ingesta_feature_engineering.py  ← Script entrenamiento del modelo
│   ├── requirements.txt                       ← Deps ML (sklearn, pandas, numpy)
│   └── models/
│       ├── rf_vulnerability_detector.joblib   ← Modelo RF entrenado (96.4%)
│       ├── tfidf_vectorizer.joblib            ← Vectorizador TF-IDF
│       └── model_metadata.joblib             ← Metadatos del entrenamiento
│
└── README.md                       ← Este archivo
```

---

## 🛠️ Setup Local

### Prerrequisitos

- **Python 3.11+**
- **Node.js 18+** y **npm** (para el Frontend)
- **Docker Desktop** (opcional, necesario si quieres correr SonarQube localmente)
- **Git**

---

### 🚀 Levantando el Backend

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/<tu-usuario>/pipeline-seguro
   cd pipeline-seguro
   ```

2. **Configurar el entorno virtual de Python:**
   ```bash
   cd backend
   python -m venv .venv
   
   # Activar en Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Activar en Linux/macOS:
   source .venv/bin/activate
   ```

3. **Instalar dependencias del Backend:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variables de Entorno del Backend:**
   Copia el archivo `.env.example` como `.env` dentro de la carpeta `backend/`:
   ```bash
   cp .env.example .env
   ```
   Abre el archivo `.env` recién creado. Para desarrollo local rápido, puedes configurar SQLite:
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./master_auth.db
   JWT_SECRET=tu_secreto_hexadecimal_generado_localmente
   DEBUG=True
   ```
   *(Nota: Para producción, la url apuntará a PostgreSQL/Supabase en formato `postgresql+asyncpg://...`)*

5. **Ejecutar Migraciones de Base de Datos (Alembic):**
   ```bash
   alembic upgrade head
   ```

6. **Poblar la base de datos con datos semilla de prueba:**
   Ejecuta el script de semilla para crear los roles (`ADMIN`, `VENDEDOR`), usuarios de prueba (`admin@gateway.com`, `vendedor@gateway.com`), módulos y menús jerárquicos:
   ```bash
   python seed_test_data.py
   ```

7. **Iniciar el servidor Backend:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *   **API local en:** `http://localhost:8000`
   *   **Documentación Interactiva (Swagger UI):** `http://localhost:8000/docs`

---

### 💻 Levantando el Frontend (Next.js SPA)

1. **Abrir una nueva terminal e ingresar a la carpeta del frontend:**
   ```bash
   cd frontend/webapp
   ```

2. **Instalar dependencias de Node.js:**
   ```bash
   npm install
   ```

3. **Iniciar el servidor de desarrollo del Frontend:**
   ```bash
   npm run dev
   ```
   *   **Aplicación web disponible en:** `http://localhost:3000`
   *   **Credenciales de prueba sembradas:**
       *   **Admin:** `admin@gateway.com` / `Admin123!`
       *   **Vendedor:** `vendedor@gateway.com` / `Vendedor123!`

---

### 🧪 Pruebas Unitarias y Estáticas

- **Correr Tests del Backend (Pytest):**
  ```bash
  cd backend
  pytest tests/ -v
  ```
- **Levantar SonarQube local en Docker (Opcional):**
  ```bash
  docker run -d --name sonarqube -p 9000:9000 sonarqube:community
  # Accede a http://localhost:9000 (admin / admin)
  ```
- **Configurar el Self-Hosted Runner (para el Pipeline):**
  En tu repositorio de GitHub ve a **Settings → Actions → Runners → New self-hosted runner** y sigue los pasos correspondientes a tu sistema operativo. El runner permitirá a GitHub Actions contactar a tu servidor local de SonarQube sin exponerlo a internet.

---

### 🔄 Flujo del Pipeline (Git)

Para disparar el flujo completo de validaciones (ML Gatekeeper + SonarQube + Pytest + Deploy):
```bash
git checkout dev
git add .
git commit -m "feat: mi cambio"
git push origin dev
# Crea un Pull Request de 'dev' hacia 'test' en GitHub 🚀
```

---

## 📡 Notificaciones de Telegram

| Evento | Mensaje |
|---|---|
| Inicio revisión ML | `⏳ [JOB 1/4] INICIO: Análisis ML de seguridad...` |
| Código seguro | `✅ [JOB 1/4] GATEKEEPER PASS: El código es seguro...` |
| Código vulnerable | `🚨 [JOB 1/4] ALERTA CRÍTICA: PR bloqueado...` |
| SonarQube iniciado | `🔍 [JOB 2/4] SONARQUBE: Iniciando análisis estático...` |
| Quality Gate pass | `✅ [JOB 2/4] SONARQUBE PASS: Sin deuda técnica crítica` |
| Quality Gate fail | `❌ [JOB 2/4] SONARQUBE FAIL: Quality Gate no superado` |
| Pytest exitoso | `✅ [JOB 3/4] PYTEST PASS: Todas las pruebas pasaron` |
| Pytest fallido | `❌ [JOB 3/4] ERROR PYTEST: Pruebas funcionales fallaron` |
| Merge realizado | `🔄 [JOB 3/4] MERGE REALIZADO: PR fusionado en test` |
| Despliegue exitoso | `🎉 [JOB 4/4] DESPLIEGUE EXITOSO: Código en producción` |
| Despliegue fallido | `❌ [JOB 4/4] ERROR DE DESPLIEGUE: Falló el webhook` |

---

<div align="center">

[🌐 Ver API en Producción](https://pipeline-seguro.onrender.com/docs) · [📊 Ver Pipeline en GitHub Actions](../../actions) · [🔍 Ver SonarQube](http://localhost:9000)

**Proyecto Parcial III — Desarrollo Seguro 2026-50**

</div>
