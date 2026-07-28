# 🛡️ Master Gateway — Sistema de Autenticación y Autorización Centralizado

<div align="center">

![Pipeline Status](https://img.shields.io/badge/Pipeline-Activo-brightgreen?style=for-the-badge&logo=github-actions)
![ML Accuracy](https://img.shields.io/badge/ML%20Accuracy-96.4%25-blue?style=for-the-badge&logo=scikit-learn)
![Python](https://img.shields.io/badge/Python-3.11-yellow?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?style=for-the-badge&logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=for-the-badge&logo=next.js)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql)
![SonarQube](https://img.shields.io/badge/SonarQube-v26.6-4E9BCD?style=for-the-badge&logo=sonarqube)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker)

**Proyecto Integrador Parcial III — Desarrollo de Software Seguro 2026-50**  
Universidad de las Fuerzas Armadas ESPE · Docente: Geovanny Cudco

**📖 Swagger UI (local):** [http://localhost:8000/docs](http://localhost:8000/docs)  
**🔍 SonarQube (local):** [http://localhost:9000](http://localhost:9000)  
**🐳 Guía Docker completa:** [DOCKER.md](./DOCKER.md)

</div>

---

## 📋 Tabla de Contenidos

- [Descripción General y Objetivo](#-descripción-general-y-objetivo)
- [Cumplimiento del Plan del Proyecto](#-cumplimiento-del-plan-del-proyecto)
- [Stack Tecnológico](#-stack-tecnológico)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Modelo de Datos (Entidad-Relación)](#-modelo-de-datos-entidad-relación)
- [Flujo de Autenticación (Doble Paso)](#-flujo-de-autenticación-doble-paso)
- [Flujo de Trabajo Git (Branches)](#-flujo-de-trabajo-git-branches)
- [Pipeline CI/CD DevSecOps — 4 Jobs](#-pipeline-cicd-devsecops--4-jobs)
- [Quality Gate SonarQube v26.6](#-quality-gate-sonarqube-v266)
- [Modelo de Machine Learning (SAST Avanzado)](#-modelo-de-machine-learning-sast-avanzado)
- [API — Endpoints Implementados](#-api--endpoints-implementados)
- [Seguridad Implementada (Shift-Left & Zero Trust)](#-seguridad-implementada-shift-left--zero-trust)
- [Notificaciones de Telegram](#-notificaciones-de-telegram)
- [GitHub Secrets Requeridos](#-github-secrets-requeridos)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Cómo Levantar el Proyecto](#️-cómo-levantar-el-proyecto)

---

## 🌟 Descripción General y Objetivo

El **Master Gateway** es un microservicio Full-Stack de **Autenticación y Autorización Centralizado**, diseñado como el eje de identidad de un ecosistema de microservicios bajo los principios de **Shift-Left Security** y **Zero Trust Architecture (ZTA)**.

### Problema que resuelve

En arquitecturas de microservicios, la fragmentación de la gestión de identidades genera silos de seguridad, duplicación de código y exposición a vulnerabilidades críticas (como Broken Access Control). Este sistema actúa como el único punto de verdad que responde:

- **¿Quién eres?** → Autenticación con JWT de doble paso
- **¿Qué puedes hacer?** → Roles y módulos asignados dinámicamente
- **¿Dónde puedes ir?** → Menú recursivo construido en tiempo de ejecución por el rol activo

### Principio Shift-Left en acción

La seguridad se integra **antes** del merge a producción, no después:

```
Commit en dev → Pull Request → ML Gatekeeper → SonarQube Quality Gate → Pytest → Merge automático a test → Promoción a main
                                    ↑                    ↑                  ↑
                          Bloquea vulnerabilidades  Bloquea deuda técnica  Tests funcionales
                             (96.4% accuracy)       (reglas OWASP/CWE)     (SQLite en memoria)
```

---

## ✅ Cumplimiento del Plan del Proyecto

La siguiente tabla mapea cada requisito del enunciado con la implementación realizada:

### Objetivos Específicos

| # | Objetivo Específico | Estado | Implementación |
|:---:|---|:---:|---|
| OE1 | Modelo de datos relacional M:N entre Usuarios y Roles | ✅ | Tablas `users`, `roles`, `user_roles` con SQLAlchemy async |
| OE2 | Estructura de menús dinámica y recursiva (Adjacency List) | ✅ | Tabla `menus` con `parent_id` + CTE en `GET /api/menus/tree` |
| OE3 | Login con selección activa de rol (Workspace Selector) | ✅ | Flujo TempToken → selección de rol → JWT definitivo por sesión |
| OE4 | Arquitectura Zero Trust con JWT para microservicios hijos | ✅ | Endpoint `POST /api/internals/validate-token` |
| OE5 | Shift-Left: pruebas de seguridad, sanitización y bcrypt | ✅ | Pytest + `bleach` + `passlib[bcrypt]` + SQLAlchemy ORM sin raw SQL |

### Requisitos Funcionales

| Requisito | Estado | Detalle |
|---|:---:|---|
| CRUD completo Usuarios y Roles | ✅ | `/api/users/*`, `/api/roles/*` con tabla pivote `user_roles` |
| Gestión de Módulos y Menús | ✅ | `/api/modules/*`, `/api/menus/*` con patrón Adjacency List |
| Pantalla Workspace Selector (selección de rol) | ✅ | Frontend Next.js con pantalla de selección post-login |
| Enrutamiento dinámico en Frontend (sin hardcodeo) | ✅ | Rutas construidas en runtime desde el JSON del menú del backend |
| Auditoría global en todos los modelos | ✅ | `BaseAudit`: `estado`, `fecha_creacion`, `fecha_actualizacion`, `creado_por`, `actualizado_por` |
| Soft Delete (nunca DELETE físico) | ✅ | `estado = 'INACTIVO'` en todos los modelos; filtro global en ORM |
| Tabla pivote con auditoría (M:N) | ✅ | `user_roles`, `role_modules`, `role_menus` con campos de auditoría propios |

### Requisitos No Funcionales y de Seguridad

| Requisito | Estado | Implementación |
|---|:---:|---|
| Zero Trust — validación en cada endpoint | ✅ | Dependencia `get_current_user` en todos los routers protegidos |
| Delegación de confianza al Master | ✅ | `POST /api/internals/validate-token` (endpoint interno Zero Trust) |
| Principio de Menor Privilegio | ✅ | JWT solo contiene permisos del rol seleccionado, no del usuario global |
| Bcrypt con factor de costo alto | ✅ | `passlib[bcrypt]` con `BCRYPT_ROUNDS=12` |
| Consultas parametrizadas (sin SQL crudo) | ✅ | 100% SQLAlchemy ORM async con parámetros vinculados |
| Gestión segura de Secrets | ✅ | `pydantic-settings` + variables de entorno + GitHub Secrets |
| SAST estático en pipeline (SonarQube) | ✅ | SonarQube Community v26.6 self-hosted + Quality Gate |
| SAST avanzado con ML (Data Mining) | ✅ | Random Forest 96.4% + AST + TF-IDF (CVEFixes dataset) |
| Notificaciones Telegram en pipeline | ✅ | Bot de Telegram integrado en los 4 jobs del pipeline |
| Estrategia de ramas Git | ✅ | `feature/* → dev → test → main` con Branch Protection Rules |
| Pipeline CI/CD con GitHub Actions | ✅ | `.github/workflows/pipeline-seguro.yml` con 4 jobs secuenciales |
| CTE para consultas recursivas de menú | ✅ | `GET /api/menus/tree` usa `WITH RECURSIVE` vía SQLAlchemy |
| Menú optimizado (sin problema N+1) | ✅ | Una sola consulta CTE devuelve el árbol completo |
| Stack Docker completo | ✅ | `docker-compose.yml`: `master_db` + `master_api` + `master_frontend` |

---

## 🔧 Stack Tecnológico

### Backend

| Tecnología | Versión | Rol |
|---|---|---|
| **Python** | 3.11 | Lenguaje principal |
| **FastAPI** | 0.115+ | Framework web async (OAuth2, validación automática) |
| **SQLAlchemy** | 2.x async | ORM — prevención SQL Injection, consultas CTE recursivas |
| **Alembic** | latest | Migraciones de base de datos |
| **PostgreSQL** | 16 | Base de datos principal (producción/Docker) |
| **SQLite** | — | Base de datos para tests (en memoria) |
| **Pydantic v2** | latest | Validación y serialización de datos |
| **pydantic-settings** | latest | Gestión segura de variables de entorno |
| **passlib[bcrypt]** | latest | Hash de contraseñas (cost factor 12) |
| **python-jose** | latest | Firma y verificación JWT (HS256) |
| **bleach** | latest | Sanitización de entradas (prevención XSS) |
| **aiosqlite** / **asyncpg** | latest | Drivers async de base de datos |
| **pytest + httpx** | latest | Tests unitarios y de integración async |

### Frontend

| Tecnología | Versión | Rol |
|---|---|---|
| **Next.js** | 15 (App Router) | SPA con enrutamiento dinámico |
| **React** | 19 | UI components |
| **TypeScript** | 5+ | Tipado estático |
| **Tailwind CSS** | 3 | Estilos utilitarios |

### DevSecOps / Infraestructura

| Tecnología | Rol |
|---|---|
| **Docker + Docker Compose** | Stack completo containerizado |
| **GitHub Actions** | Pipeline CI/CD automatizado |
| **SonarQube Community v26.6** | SAST estático self-hosted |
| **scikit-learn (Random Forest)** | SAST avanzado ML (CVEFixes dataset) |
| **Telegram Bot API** | Notificaciones en tiempo real del pipeline |
| **GitHub Self-Hosted Runner** | Acceso a SonarQube local desde el pipeline |

---

## 🏗️ Arquitectura del Sistema

### Arquitectura de la Aplicación (Docker Stack)

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network: gateway_net               │
│                                                             │
│  ┌──────────────────┐       ┌──────────────────────────┐   │
│  │  master_frontend  │       │    master_api (FastAPI)   │   │
│  │  Next.js 15       │──────▶│    Puerto: 8000           │   │
│  │  Puerto: 3000     │       │    /api/auth/*            │   │
│  └──────────────────┘       │    /api/users/*           │   │
│                             │    /api/roles/*           │   │
│                             │    /api/modules/*         │   │
│                             │    /api/menus/*           │   │
│                             │    /api/internals/*       │   │
│                             └──────────┬───────────────┘   │
│                                        │                    │
│                             ┌──────────▼───────────────┐   │
│                             │   master_db (PostgreSQL)  │   │
│                             │   Puerto: 5432            │   │
│                             └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Arquitectura del Pipeline DevSecOps

```
┌─────────────────────────────────────────────────────────────────────────────┐
│               DEVELOPER  (rama dev / feature/*)                              │
│               git push origin dev → Pull Request → test                     │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │  PR abierto
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                   GITHUB ACTIONS: pipeline-seguro.yml                       │
│                                                                             │
│  ┌──────────────────┐                                                       │
│  │  JOB 1           │  runs-on: ubuntu-latest                              │
│  │  Gatekeeper ML   │─── VULNERABLE? ──▶ Cerrar PR + Issue + Telegram 🚨  │
│  │  (RF + AST)      │─── SEGURO?    ──┐                                    │
│  └──────────────────┘                 │                                    │
│                                       ▼                                    │
│  ┌──────────────────┐                                                       │
│  │  JOB 2           │  runs-on: self-hosted (accede a localhost:9000)      │
│  │  SonarQube SAST  │─── GATE FAIL? ──▶ Notificar Telegram ❌              │
│  │  Quality Gate    │─── GATE PASS? ──┐                                    │
│  └──────────────────┘                 │                                    │
│                                       ▼                                    │
│  ┌──────────────────┐                                                       │
│  │  JOB 3           │  runs-on: ubuntu-latest                              │
│  │  Merge + Pytest  │─── FAIL? ──▶ Label 'tests-failed' + Telegram ❌     │
│  │  (rama test)     │─── PASS? ──┐                                         │
│  └──────────────────┘            │                                         │
│                                  ▼                                         │
│  ┌──────────────────┐                                                       │
│  │  JOB 4           │  runs-on: ubuntu-latest                              │
│  │  Promoción Main  │─── Crea PR test→main + merge automático              │
│  │  (rama main)     │─── Notificación final a Telegram 🎉                 │
│  └──────────────────┘                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│       rama main — código 100% verificado (ML + SonarQube + Pytest)          │
│       Listo para despliegue en cualquier PaaS (Render, Railway, etc.)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Modelo de Datos (Entidad-Relación)

El modelo implementa exactamente las relaciones requeridas en el enunciado:

```
┌────────────┐       ┌─────────────┐       ┌────────────┐
│   users    │ M:N   │  user_roles │  M:N  │   roles    │
│────────────│◀──────│─────────────│──────▶│────────────│
│ id (UUID)  │       │ user_id     │       │ id (UUID)  │
│ email      │       │ role_id     │       │ nombre     │
│ pwd_hash   │       │ fecha_creac │       │ descripcion│
│ BaseAudit  │       │ creado_por  │       │ BaseAudit  │
└────────────┘       └─────────────┘       └──────┬─────┘
                                                   │ M:N
                                      ┌────────────▼─────┐
                                      │  role_modules    │
                                      │────────────────  │
                                      │ role_id          │
                                      │ module_id        │
                                      └────────┬─────────┘
                                               │
                          ┌────────────┐       │       ┌─────────────────────┐
                          │  modules   │◀──────┘  M:N  │     role_menus      │
                          │────────────│               │─────────────────────│
                          │ id (UUID)  │               │ role_id             │
                          │ nombre     │               │ menu_id             │
                          │ BaseAudit  │               └──────────┬──────────┘
                          └────────────┘                          │
                                                                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     menus  (Adjacency List — Estructura Recursiva)            │
│──────────────────────────────────────────────────────────────────────────────│
│ id (UUID)   nombre   url   icono   orden   modulo_id   parent_id   BaseAudit │
│                                                                               │
│  NULL parent_id  → Menú Principal (raíz)                                     │
│  parent_id != NULL → Submenú o Item hoja (con url)                           │
│                                                                               │
│  Consulta árbol: WITH RECURSIVE CTE → O(n) query, sin problema N+1          │
└──────────────────────────────────────────────────────────────────────────────┘
```

### BaseAudit — Campos de Auditoría Global

Todos los modelos heredan de `BaseAudit`, garantizando trazabilidad completa:

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador único generado automáticamente |
| `estado` | Enum | `ACTIVO` / `INACTIVO` — Soft Delete (nunca DELETE físico) |
| `fecha_creacion` | Timestamp | Generado automáticamente al insertar (ORM hook) |
| `fecha_actualizacion` | Timestamp | Actualizado automáticamente en cada UPDATE (ORM hook) |
| `creado_por` | UUID (FK) | Usuario que creó el registro (null si auto-registro) |
| `actualizado_por` | UUID (FK) | Usuario que realizó la última modificación |

---

## 🔐 Flujo de Autenticación (Doble Paso)

El sistema implementa el patrón de **Workspace Selector** requerido: el usuario elige explícitamente el rol con el que operará en esa sesión.

```
1. POST /api/auth/login
   ├── Credenciales (email + password)
   ├── Verifica bcrypt hash
   ├── Genera TempToken (corta duración: 5 min)
   └── Devuelve: { temp_token, roles: [{ id, nombre }] }

2. Frontend → Pantalla "Selecciona tu Espacio de Trabajo"
   └── Usuario elige el rol activo para esta sesión

3. POST /api/auth/select-role
   ├── TempToken + roleId
   ├── Valida que el usuario tenga ese rol asignado
   ├── Genera JWT definitivo (solo con permisos de ESE rol)
   └── Devuelve: { access_token, refresh_token }

4. GET /api/menus/tree  (con JWT en header)
   ├── Decodifica JWT → extrae roleId
   ├── Ejecuta CTE recursiva filtrando por roleId
   └── Devuelve árbol jerárquico de módulos, submenús e items

5. Frontend inyecta rutas dinámicamente (sin hardcodeo)
   └── Navegación construida 100% en runtime desde el JSON del backend
```

### Zero Trust — Validación para Microservicios Hijos

```
Microservicio Hijo (ej. Ventas) → POST /api/internals/validate-token
                                        ├── Header: Authorization: Bearer <JWT>
                                        ├── Verifica firma del JWT
                                        └── Devuelve: { valid, userId, roleId }
                                            (sin exponer datos sensibles)
```

---

## 🌿 Flujo de Trabajo Git (Branches)

```
  feature/* ──PR──▶  dev  ──PR──▶  test  ──PR auto──▶  main
                      │              │                    │
               Desarrollo       Staging QA          Producción
                                    │
                        Pipeline se dispara aquí
                        (PR dev → test)
```

| Rama | Propósito | Protección |
|---|---|---|
| `feature/*` | Funcionalidades individuales | Push directo permitido |
| `dev` | Integración de desarrollo | Push directo permitido |
| `test` | Staging. Solo código que pasó ML + SonarQube + Pytest | **Branch Protected** — solo merge via pipeline |
| `main` | Producción. Código 100% verificado | **Branch Protected** — solo merge automático del Job 4 |

> **Configuración requerida:** `main` y `test` tienen Branch Protection Rules activas. En GitHub: Settings → Actions → General → **Read and write permissions** + **Allow GitHub Actions to create and approve pull requests**.

---

## 🔄 Pipeline CI/CD DevSecOps — 4 Jobs

### JOB 1 — Gatekeeper de Seguridad ML

**Entorno:** `runs-on: ubuntu-latest` (GitHub Cloud)

**¿Qué hace?** Analiza el diff del PR con un modelo de Machine Learning entrenado en vulnerabilidades reales antes de permitir cualquier merge.

```yaml
gatekeeper-security-check:
  steps:
    - Checkout del código
    - Notificar inicio vía Telegram ⏳
    - Setup Python 3.11 + scikit-learn==1.8.0 + joblib
    - Extraer diff del PR (gh pr diff)
    - Ejecutar scripts/analizador_ci.py
    - VULNERABLE → Comentar PR + Cerrar PR + Abrir Issue + Telegram 🚨
    - SEGURO    → Notificar éxito vía Telegram ✅
```

**Motor de decisión en 3 capas:**

| Capa | Mecanismo | Comportamiento |
|---|---|---|
| **Capa 1** | Random Forest (96.4% accuracy) sobre TF-IDF | Bloquea si pred=1 O probabilidad ≥ 50% |
| **Capa 2** | AST determinista (`pickle.loads`, `os.system`, `hashlib.md5`, `yaml.load`) | Bloquea siempre que detecta patrón |
| **Capa 3** | Heurísticas de texto (SQLi, XSS keywords) | Añade detalle al reporte sin bloquear solo |

---

### JOB 2 — Análisis SAST SonarQube Community

**Entorno:** `runs-on: self-hosted` ← tu PC local donde corre SonarQube

**¿Por qué self-hosted?** SonarQube corre en tu red local en `http://localhost:9000`. Al instalar el self-hosted runner en tu PC, GitHub Actions accede directamente sin exponer puertos a internet ni usar Ngrok.

```yaml
sonarqube-analysis:
  needs: gatekeeper-security-check
  runs-on: self-hosted
  steps:
    - Checkout (fetch-depth: 0 para análisis de blame)
    - Notificar inicio vía Telegram 🔍
    - Ejecutar SonarQube Scanner (sonarsource/sonarqube-scan-action)
      - sonar.projectKey=Master-Gateway
      - sonar.sources=backend/app
      - sonar.tests=backend/tests
      - sonar.python.version=3.11
    - Verificar Quality Gate (sonarsource/sonarqube-quality-gate-action)
    - FAIL → Notificar Telegram ❌
    - PASS → Notificar Telegram ✅
```

---

### JOB 3 — Merge Automático y Pytest

**Entorno:** `runs-on: ubuntu-latest`

```yaml
auto-merge-and-test:
  needs: [gatekeeper-security-check, sonarqube-analysis]
  steps:
    - Setup Python 3.11 + instalar backend/requirements.txt
    - Ejecutar pytest backend/tests/ -v
      (SQLite en memoria — sin necesidad de Supabase ni conexión externa)
    - FAIL → Label 'tests-failed' en el PR + Telegram ❌
    - PASS → gh pr merge --admin + Telegram ✅
```

**Tests cubiertos:**

| Archivo | Qué prueba |
|---|---|
| `test_auth.py` | Login doble paso, TempToken → JWT definitivo, mensaje HTTP 401 genérico en fallo |
| `test_users.py` | Validación contraseña fuerte (Shift-Left), sanitización XSS con `bleach` |
| `test_roles.py` | Validación regex nombre de rol, prevención de eliminar rol `ADMIN` |
| `test_menus.py` | Árbol recursivo de menús vía CTE, detección de ciclos en `parent_id` |

---

### JOB 4 — Promoción a Main

**Entorno:** `runs-on: ubuntu-latest`

```yaml
promote-to-main:
  needs: auto-merge-and-test
  steps:
    - Checkout rama 'test' (fetch-depth: 0)
    - Crear PR automático test → main (si no existe)
    - gh pr merge --admin (merge commit)
    - Notificación final a Telegram 🎉 o ❌
```

> El código en `main` queda listo para despliegue manual en cualquier PaaS (Render, Railway, etc.) cuando el equipo lo decida.

---

## 📊 Quality Gate SonarQube v26.6

Configurado en `http://localhost:9000` → **Quality Gates** → `Master-Gateway-QG`.

El proyecto usa **MQR Mode** (Multi-Quality Rule, modo por defecto en v26.6):

| Métrica | Clave interna | Condición | Umbral |
|---|---|:---:|:---:|
| **Security Issues** | `software_quality_security_issues` | `>` | `0` |
| **Reliability Issues** | `software_quality_reliability_issues` | `>` | `5` |
| **Maintainability Issues** | `software_quality_maintainability_issues` | `>` | `15` |
| **Coverage** | `coverage` | `<` | `60%` |
| **Duplicated Lines (%)** | `duplicated_lines_density` | `>` | `10%` |

> **¿Por qué MQR Mode?** SonarQube v26.6 reemplaza las métricas clásicas (`bugs`, `vulnerabilities`, `code_smells`) por el modelo de **Software Qualities**. El Quality Gate bloquea el pipeline si alguna condición no se cumple.

---

## 🤖 Modelo de Machine Learning (SAST Avanzado)

> **Restricción cumplida:** No se usan LLMs. Todo el análisis es **ML clásico** entrenado localmente sobre CVEFixes. Cumple con el requisito de "script de Python que consuma un modelo ML con datasets de CWEs".

### Dataset y Algoritmo

| Componente | Detalle |
|---|---|
| **Dataset base** | CVEFixes — vulnerabilidades reales de repositorios Git |
| **Datos sintéticos** | +1,200 muestras (Juliet Test Suite NSA/NIST) |
| **Vectorizador** | TF-IDF (Term Frequency–Inverse Document Frequency) |
| **Clasificador** | `RandomForestClassifier(random_state=42)` |
| **Accuracy** | **96.43%** — Validación cruzada estratificada 10-fold |
| **Salida** | Código de salida `0` (seguro) o `1` (vulnerable) |

### 7 Features AST Extraídas del Código

| Feature | Descripción | Vulnerabilidades detectadas |
|---|---|---|
| `ast_depth` | Profundidad máxima del árbol AST | General |
| `dangerous_func_count` | Llamadas a `eval`, `exec`, `os.system`, `subprocess.Popen` | Command Injection |
| `total_calls` | Total de llamadas a funciones | General |
| `num_imports` | Número de sentencias `import` | General |
| `has_string_concat` | Concatenación de strings | SQL Injection, XSS |
| `num_exception_handlers` | Bloques `except` (supresión de errores) | General |
| `has_hardcoded_secret` | Credencial con valor literal en el código | Secretos expuestos |

### Categorías de Vulnerabilidades Detectadas

| Categoría | Tipo | Método de detección |
|---|---|---|
| CWE-89 | SQL Injection | AST (`has_string_concat`) + Heurística |
| CWE-78 | Command Injection (`eval`, `exec`, `os.system`) | AST + Heurística |
| CWE-502 | Deserialización Insegura (`pickle.loads`, `yaml.load`) | AST + Heurística |
| CWE-22 | Path Traversal (`open(concat)`, `open(f-string)`) | AST especializado |
| CWE-798 | Secretos Hardcodeados + Criptografía Débil (`md5`, `sha1`) | AST + Heurística |
| CWE-79 | XSS (concat HTML) + SSRF (URL dinámica) | AST + Heurística |

---

## 🔌 API — Endpoints Implementados

Todos los endpoints (excepto `/api/auth/login`) requieren JWT válido en el header `Authorization: Bearer <token>`.

### Autenticación (`/api/auth/`)

| Método | Endpoint | Descripción | Seguridad |
|---|---|---|---|
| `POST` | `/api/auth/login` | Credenciales → TempToken + lista de roles | HTTP 401 genérico (no revela si falló usuario o contraseña) |
| `POST` | `/api/auth/select-role` | TempToken + roleId → JWT definitivo | JWT solo contiene permisos del rol seleccionado |
| `POST` | `/api/auth/refresh-token` | Genera nuevo JWT con Refresh Token | Revocación inmediata si se detecta reutilización |
| `POST` | `/api/auth/logout` | Invalida tokens activos en BD | Corte inmediato de sesión |

### Validación Interna Zero Trust (`/api/internals/`)

| Método | Endpoint | Descripción | Seguridad |
|---|---|---|---|
| `POST` | `/api/internals/validate-token` | Endpoint para que microservicios hijos validen JWT | Solo devuelve `valid`, `userId`, `roleId` — sin datos sensibles |

### Usuarios (`/api/users/`)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/users` | Lista paginada de usuarios activos |
| `GET` | `/api/users/{id}` | Detalle de usuario (sin `password_hash`) |
| `POST` | `/api/users` | Crear usuario (bcrypt hash automático, validación Shift-Left) |
| `PUT` | `/api/users/{id}` | Actualizar usuario (ORM actualiza `fecha_actualizacion`) |
| `DELETE` | `/api/users/{id}` | Soft Delete — cambia `estado` a `INACTIVO` |
| `POST` | `/api/users/{id}/roles` | Asignar rol a usuario (inserta en tabla pivote) |
| `DELETE` | `/api/users/{id}/roles/{roleId}` | Desasignar rol (elimina de tabla pivote) |

### Roles (`/api/roles/`)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/roles` | Lista de roles activos |
| `GET` | `/api/roles/{id}` | Detalle de un rol |
| `POST` | `/api/roles` | Crear rol (validación regex del nombre) |
| `PUT` | `/api/roles/{id}` | Actualizar rol |
| `DELETE` | `/api/roles/{id}` | Soft Delete — previene eliminar si hay usuarios activos asignados |
| `POST` | `/api/roles/{id}/modules` | Asignar módulo al rol |
| `POST` | `/api/roles/{id}/menus` | Asignar ítem de menú al rol |
| `DELETE` | `/api/roles/{id}/users/{userId}` | Rompe relación M:N en tabla pivote |

### Módulos (`/api/modules/`)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/modules` | Lista módulos activos |
| `GET` | `/api/modules/{id}` | Detalle de módulo |
| `POST` | `/api/modules` | Crear módulo |
| `PUT` | `/api/modules/{id}` | Actualizar módulo |
| `DELETE` | `/api/modules/{id}` | Soft Delete |

### Menús — Árbol Recursivo (`/api/menus/`)

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/menus/tree` | **Árbol completo** del rol del JWT — via CTE recursiva (sin N+1) |
| `GET` | `/api/menus` | Lista plana de menús |
| `POST` | `/api/menus` | Crear menú/submenú/ítem (`parent_id` null = raíz, `url` null = no es hoja) |
| `PUT` | `/api/menus/{id}` | Actualizar menú (valida que no genere ciclos en `parent_id`) |
| `DELETE` | `/api/menus/{id}` | Soft Delete |

---

## 🔒 Seguridad Implementada (Shift-Left & Zero Trust)

| Requisito | Implementación | Detalles |
|---|---|---|
| **Hash de contraseñas** | `passlib[bcrypt]` | `BCRYPT_ROUNDS=12` — resistente a fuerza bruta |
| **JWT Zero Trust** | `python-jose[cryptography]` | Doble paso: TempToken (5 min) → JWT definitivo (30 min) |
| **Menor Privilegio** | JWT por rol | Solo permisos del rol seleccionado, no del usuario global |
| **Consultas seguras** | SQLAlchemy ORM async | Sin string interpolation — parámetros vinculados internamente |
| **Gestión de Secrets** | `pydantic-settings` + `.env` | Nunca hardcodeados; GitHub Secrets en el pipeline |
| **Login genérico** | HTTP 401 unificado | No revela si falló usuario o contraseña |
| **Ocultar contraseña** | Serialización Pydantic | `password_hash` excluido de todos los responses |
| **Sanitización XSS** | `bleach` | Limpieza de entradas en campos de texto libre |
| **Validación de input** | Pydantic v2 | `EmailStr`, regex, longitudes máximas, tipos estrictos |
| **Soft Delete global** | `BaseAudit.estado` | Nunca DELETE físico; filtro automático `estado='ACTIVO'` |
| **Auditoría completa** | `BaseAudit` | Trazabilidad en usuarios, roles, módulos, menús y tablas pivote |
| **Revocación de tokens** | Tabla `revoked_tokens` | Logout e invalidación inmediata ante reutilización de Refresh Token |

### Variables de Entorno Requeridas

```env
# ── Docker Compose (recomendado) ─────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@master_db:5432/master

# ── Desarrollo local con SQLite (sin Docker) ─────────────────────────────────
DATABASE_URL=sqlite+aiosqlite:///./master_auth.db

# ── Producción con Supabase ───────────────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:<PASSWORD>@db.<REF>.supabase.co:5432/postgres

# ── JWT ──────────────────────────────────────────────────────────────────────
# Generar con: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=<secreto_fuerte_min_64_chars>
JWT_ALGORITHM=HS256
TEMP_TOKEN_EXPIRE_MINUTES=5
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── Bcrypt ────────────────────────────────────────────────────────────────────
BCRYPT_ROUNDS=12

# ── App ───────────────────────────────────────────────────────────────────────
DEBUG=False
```

---

## 📡 Notificaciones de Telegram

El pipeline envía mensajes en tiempo real a un grupo de Telegram con cada evento del CI/CD:

| Evento | Mensaje |
|---|---|
| Inicio análisis ML | `⏳ [JOB 1/4] INICIO: Análisis ML de seguridad en curso...` |
| ML → Código seguro | `✅ [JOB 1/4] GATEKEEPER PASS: El código es seguro` |
| ML → Código vulnerable | `🚨 [JOB 1/4] ALERTA CRÍTICA: PR bloqueado — vulnerabilidad detectada` |
| SonarQube iniciado | `🔍 [JOB 2/4] SONARQUBE: Iniciando análisis estático...` |
| Quality Gate pass | `✅ [JOB 2/4] SONARQUBE PASS: Sin deuda técnica crítica` |
| Quality Gate fail | `❌ [JOB 2/4] SONARQUBE FAIL: Quality Gate no superado` |
| Pytest exitoso | `✅ [JOB 3/4] PYTEST PASS: Todas las pruebas pasaron` |
| Pytest fallido | `❌ [JOB 3/4] ERROR PYTEST: Pruebas funcionales fallaron` |
| Merge a test | `🔄 [JOB 3/4] MERGE REALIZADO: PR fusionado en rama 'test'` |
| Promoción a main OK | `🎉 [JOB 4/4] PIPELINE COMPLETADO: código en 'main' verificado` |
| Promoción a main FAIL | `❌ [JOB 4/4] ERROR EN PROMOCIÓN: Falló la fusión hacia 'main'` |

---

## 🔑 GitHub Secrets Requeridos

| Secret | Descripción | Cómo obtenerlo |
|---|---|---|
| `TELEGRAM_TOKEN` | Token del bot de Telegram | [@BotFather](https://t.me/BotFather) → `/newbot` |
| `TELEGRAM_CHAT_ID` | ID del grupo/chat donde se notifica | [@userinfobot](https://t.me/userinfobot) |
| `SONAR_TOKEN` | Token de usuario SonarQube | SonarQube → My Account → Security → Generate Token |
| `SONAR_HOST_URL` | URL del servidor SonarQube | `http://localhost:9000` (accedido por runner local) |
| `GITHUB_TOKEN` | Gestión de PRs e Issues | Automático en GitHub Actions |

> **Configuración requerida en GitHub:**  
> Settings → Actions → General → Workflow permissions:  
> ✅ Read and write permissions  
> ✅ Allow GitHub Actions to create and approve pull requests

> **Self-hosted runner:**  
> Settings → Actions → Runners → New self-hosted runner → sigue los pasos para Windows.  
> El runner instalado en tu PC ejecuta el Job 2 (SonarQube) accediendo a `http://localhost:9000` directamente.

---

## 📁 Estructura del Repositorio

```
Proyecto-Master-Gateway-/
│
├── .github/
│   └── workflows/
│       └── pipeline-seguro.yml       ← Pipeline CI/CD (4 Jobs DevSecOps)
│
├── backend/
│   ├── Dockerfile                    ← Imagen Docker (non-root, python:3.11-slim)
│   ├── requirements.txt              ← FastAPI + JWT + SQLAlchemy + pytest + bleach
│   ├── .env.example                  ← Plantilla de variables de entorno
│   ├── alembic.ini                   ← Configuración Alembic
│   ├── seed_test_data.py             ← Datos iniciales (roles, usuarios, módulos, menús)
│   ├── alembic/
│   │   └── versions/                 ← Migraciones de base de datos
│   ├── app/
│   │   ├── main.py                   ← Entry point FastAPI
│   │   ├── core/
│   │   │   ├── config.py             ← Variables de entorno (pydantic-settings)
│   │   │   ├── database.py           ← Engine async SQLAlchemy + SessionLocal
│   │   │   ├── security.py           ← JWT encode/decode + bcrypt hash
│   │   │   └── dependencies.py       ← get_db, get_current_user (Depends)
│   │   ├── models/
│   │   │   ├── base.py               ← BaseAudit (soft delete + auditoría global)
│   │   │   ├── user.py               ← Modelo Usuario
│   │   │   ├── role.py               ← Modelo Rol
│   │   │   ├── module.py             ← Modelo Módulo
│   │   │   ├── menu.py               ← Modelo Menú (Adjacency List)
│   │   │   ├── user_role.py          ← Tabla pivote M:N Usuarios-Roles
│   │   │   ├── role_module.py        ← Tabla pivote M:N Roles-Módulos
│   │   │   └── role_menu.py          ← Tabla pivote M:N Roles-Menús
│   │   ├── schemas/
│   │   │   └── auth.py, user.py, role.py, module.py, menu.py
│   │   ├── services/
│   │   │   └── auth_service.py, user_service.py, role_service.py, ...
│   │   └── api/
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── auth.py           ← /api/auth/*
│   │           ├── internals.py      ← /api/internals/validate-token (Zero Trust)
│   │           ├── users.py          ← /api/users/*
│   │           ├── roles.py          ← /api/roles/*
│   │           ├── modules.py        ← /api/modules/*
│   │           └── menus.py          ← /api/menus/* + /api/menus/tree (CTE)
│   └── tests/
│       ├── conftest.py               ← BD SQLite en memoria + cliente HTTP async
│       ├── test_auth.py              ← Login doble paso, JWT, mensajes genéricos
│       ├── test_users.py             ← Contraseña fuerte, sanitización XSS
│       ├── test_roles.py             ← Validación regex, prevención eliminar ADMIN
│       └── test_menus.py             ← CTE recursiva, detección de ciclos
│
├── frontend/
│   └── webapp/
│       ├── Dockerfile                ← Imagen Docker (Next.js 15)
│       ├── src/                      ← Código fuente Next.js (App Router)
│       └── package.json
│
├── scripts/
│   ├── analizador_ci.py              ← Gatekeeper ML (Random Forest + AST, 3 capas)
│   └── generar_diff.py               ← Utilidad para testing local del gatekeeper
│
├── pipeline/
│   ├── fase1_ingesta_feature_engineering.py  ← Script de entrenamiento del modelo
│   ├── requirements.txt                       ← Deps ML (sklearn, pandas, numpy)
│   └── models/
│       ├── rf_vulnerability_detector.joblib   ← Modelo RF entrenado (96.4%)
│       ├── tfidf_vectorizer.joblib            ← Vectorizador TF-IDF
│       └── model_metadata.joblib             ← Metadatos del entrenamiento
│
├── docker-compose.yml                ← Stack completo: DB + API + Frontend
├── sonar-project.properties          ← Configuración del proyecto SonarQube
├── DOCKER.md                         ← Guía completa de despliegue con Docker
└── README.md                         ← Este archivo
```

---

## 🛠️ Cómo Levantar el Proyecto

Existen dos formas de levantar el proyecto. La **Opción 1 con Docker Compose** es la recomendada ya que levanta el stack completo en minutos con un solo comando.

### Prerrequisitos

| Opción | Herramientas necesarias |
|---|---|
| **Opción 1 — Docker** | Docker Desktop, Git |
| **Opción 2 — Manual** | Python 3.11+, Node.js 18+, npm, Git |

---

### 🐳 Opción 1: Levantar con Docker Compose (Recomendado)

Esta opción levanta automáticamente tres contenedores en red compartida:
- `master_db` → PostgreSQL 16
- `master_api` → FastAPI (aplica migraciones y seed al iniciar)
- `master_frontend` → Next.js 15

#### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/cmbonifaz/Proyecto-Master-Gateway-.git
cd Proyecto-Master-Gateway-
```

#### Paso 2: Configurar el archivo de entorno del backend

```bash
# En Windows (PowerShell):
Copy-Item backend\.env.example backend\.env

# En Linux/macOS:
cp backend/.env.example backend/.env
```

Abre `backend/.env` y asegúrate de que `DATABASE_URL` apunte al contenedor `master_db`:

```env
# IMPORTANTE: Para Docker Compose, usa el nombre del servicio "master_db" como host
DATABASE_URL=postgresql+asyncpg://postgres:postgres@master_db:5432/master

# Generar JWT_SECRET con: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=tu_secreto_hexadecimal_de_al_menos_32_caracteres
JWT_ALGORITHM=HS256
TEMP_TOKEN_EXPIRE_MINUTES=5
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
DEBUG=False
```

> ⚠️ **NUNCA** subas el archivo `.env` al repositorio. Está en `.gitignore`.

#### Paso 3: Levantar todos los contenedores

Desde la raíz del proyecto:

```bash
docker compose up --build -d
```

> **Nota:** Al iniciar, `master_api` ejecuta automáticamente `alembic upgrade head` y `python seed_test_data.py`. Puedes ver el progreso con `docker compose logs -f master_api`.

#### Paso 4: Verificar que todos los servicios están corriendo

```bash
docker compose ps
```

Deberías ver los tres contenedores con estado `running` o `healthy`.

#### Paso 5 (Solo si es necesario): Ejecutar migraciones y seed manualmente

Si el contenedor `master_api` reinicia por error de conexión (por ejemplo, si el `.env` tenía la URL de Supabase en lugar de `master_db`):

```bash
# 1. Asegúrate de que backend/.env tiene DATABASE_URL=...@master_db...
# 2. Recrea el contenedor para que tome los nuevos valores del .env
docker compose up -d --force-recreate master_api

# 3. (Opcional) Si aún necesitas forzar las migraciones manualmente:
docker compose exec master_api alembic upgrade head
docker compose exec master_api python seed_test_data.py
```

#### Paso 6: Acceder al sistema

| Servicio | URL |
|---|---|
| **Frontend (Next.js)** | [http://localhost:3000](http://localhost:3000) |
| **Backend API (FastAPI)** | [http://localhost:8000](http://localhost:8000) |
| **Documentación Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) |

#### Comandos útiles de gestión

```bash
# Ver logs en tiempo real de la API
docker compose logs -f master_api

# Detener todos los contenedores
docker compose down

# Detener y eliminar volúmenes (borra los datos de la BD)
docker compose down -v

# Reiniciar un servicio específico
docker compose restart master_api
```

---

### 💻 Opción 2: Levantamiento Manual (Desarrollo local sin Docker)

Ideal para desarrollo rápido. Usa SQLite en archivo local (sin necesidad de PostgreSQL).

#### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/cmbonifaz/Proyecto-Master-Gateway-.git
cd Proyecto-Master-Gateway-
```

#### Paso 2: Configurar y levantar el Backend (FastAPI)

```bash
# Ingresar a la carpeta del backend
cd backend

# Crear el entorno virtual de Python
python -m venv .venv

# Activar el entorno virtual
# En Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate

# Instalar todas las dependencias
pip install -r requirements.txt
```

Configurar variables de entorno:

```bash
# En Windows (PowerShell):
Copy-Item .env.example .env

# En Linux/macOS:
cp .env.example .env
```

Edita `backend/.env` para usar SQLite local:

```env
DATABASE_URL=sqlite+aiosqlite:///./master_auth.db
JWT_SECRET=tu_secreto_hexadecimal_generado_localmente
JWT_ALGORITHM=HS256
TEMP_TOKEN_EXPIRE_MINUTES=5
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BCRYPT_ROUNDS=12
DEBUG=True
```

Ejecutar migraciones y datos iniciales:

```bash
alembic upgrade head
python seed_test_data.py
```

Iniciar el servidor de desarrollo:

```bash
uvicorn app.main:app --reload --port 8000
```

- **API:** `http://localhost:8000`
- **Swagger UI:** `http://localhost:8000/docs`

#### Paso 3: Levantar el Frontend (Next.js SPA)

Abre una **nueva terminal** desde la raíz del proyecto:

```bash
cd frontend/webapp

# Instalar dependencias de Node.js
npm install

# Iniciar servidor de desarrollo
npm run dev
```

- **Aplicación web:** `http://localhost:3000`

---

### 🔑 Credenciales de Prueba (Sembradas automáticamente)

| Rol | Email | Contraseña |
|---|---|---|
| **ADMIN** | `admin@gateway.com` | `AdminPass123!` |
| **VENDEDOR** | `vendedor@gateway.com` | `Vendedor123!` |
| **BODEGUERO** | `bodega@gateway.com` | `Bodega123!` |
| **RRHH** | `rrhh@gateway.com` | `RRHH123!` |

---

### 🧪 Ejecutar las Pruebas Unitarias

```bash
cd backend

# Activar entorno virtual si no está activo
.\.venv\Scripts\Activate.ps1   # Windows
source .venv/bin/activate      # Linux/macOS

# Ejecutar todos los tests con detalle
pytest tests/ -v

# Ejecutar con reporte de cobertura
pytest tests/ -v --cov=app --cov-report=term-missing
```

> Los tests usan **SQLite en memoria** — no requieren conexión a PostgreSQL ni Supabase.

---

### 🔍 Levantar SonarQube Local (Para el Pipeline)

```bash
# Levantar SonarQube Community en Docker
docker run -d --name sonarqube -p 9000:9000 sonarqube:community

# Accede a http://localhost:9000 (usuario: admin / contraseña: admin)
```

Luego, registra el self-hosted runner en tu PC:
> GitHub → Settings → Actions → Runners → **New self-hosted runner** → Sigue los pasos para Windows.

---

### 🔄 Disparar el Pipeline Completo (Git Flow)

```bash
# Trabajar en la rama de desarrollo
git checkout dev
git add .
git commit -m "feat: descripción del cambio"
git push origin dev

# En GitHub: crear un Pull Request de 'dev' → 'test'
# El pipeline se dispara automáticamente 🚀
```

---

<div align="center">

[📖 Swagger UI local](http://localhost:8000/docs) · [📊 Pipeline en GitHub Actions](../../actions) · [🔍 SonarQube local](http://localhost:9000) · [🐳 Guía Docker completa](./DOCKER.md)

**Proyecto Integrador Parcial III — Desarrollo de Software Seguro 2026-50**  
Universidad de las Fuerzas Armadas ESPE

</div>
