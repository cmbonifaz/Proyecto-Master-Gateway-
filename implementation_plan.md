# 🛡️ Plan de Implementación — Proyecto Parcial III (Desarrollo Seguro 2026-50)

> **Estado:** Pendiente de aprobación  
> **Stack:** Python · FastAPI · PostgreSQL · SQLAlchemy · JWT · SonarQube Community · GitHub Actions · Render  
> **Modelo ML:** Random Forest ya entrenado (96.4% accuracy) — reutilizado del proyecto anterior

---

## 📌 Contexto y Objetivo

Migrar el proyecto **LiveSeat** (sistema de reservas) hacia un **Microservicio Maestro de Autenticación y Autorización** siguiendo la especificación del PDF del parcial. Se mantiene el pipeline ML/SAST existente (el más valioso) y se reconstruye el dominio de negocio.

### Decisiones de arquitectura confirmadas
- **Backend:** FastAPI (Python puro) → el modelo ML ya lee solo `.py`, coherente con el SAST
- **SAST estático:** SonarQube Community (auto-hosted) en lugar de SonarCloud
- **Microservicios:** FastAPI soporta múltiples `APIRouter`, cada uno como "microservicio" lógico montado en el Master
- **BD:** PostgreSQL (soporta `WITH RECURSIVE` nativo para menús)
- **Auth:** JWT de doble paso (TempToken → JWT definitivo por rol)

---

## 📂 Fase 0 — Limpieza del Repositorio

### Archivos a ELIMINAR
```
backend/app/api/endpoints/eventos.py
backend/app/api/endpoints/reservas.py
backend/app/schemas/event.py
backend/app/schemas/reservation.py
backend/app/models/domain.py
backend/app/db/repository.py
backend/app/services/event_service.py
backend/app/services/reservation_service.py
backend/app/prueba_seguridad.py
backend/backend_docs.md
pdf_content.txt
pdf_content_utf8.txt
vulnerable.py
```

### Archivos a CONSERVAR sin cambios
```
scripts/analizador_ci.py          ← SAST ML Gatekeeper (reutilizar 100%)
scripts/generar_diff.py           ← Utilidad de testing
pipeline/models/*.joblib          ← Modelo RF entrenado
pipeline/requirements.txt         ← Deps ML
pipeline/fase1_ingesta_*.py       ← Script entrenamiento
pipeline/__init__.py
.gitignore
backend/Dockerfile                ← Solo adaptar entrypoint
```

### Archivos a MODIFICAR
```
.github/workflows/pipeline-seguro.yml   ← Adaptar + agregar SonarQube
backend/requirements.txt                ← Ampliar con JWT/ORM
backend/app/main.py                     ← Cambiar título y routers
backend/app/api/router.py               ← Nuevos routers
backend/tests/test_main.py              ← Nuevos tests de auth
README.md                               ← Actualizar documentación
```

---

## 📂 Fase 1 — Nueva Estructura del Backend

### Estructura objetivo
```
backend/
├── Dockerfile
├── requirements.txt
├── alembic.ini
├── alembic/
│   └── versions/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py          ← Variables de entorno (pydantic-settings)
│   │   ├── database.py        ← Engine + SessionLocal SQLAlchemy
│   │   ├── security.py        ← JWT encode/decode, bcrypt hash
│   │   └── dependencies.py    ← get_db, get_current_user (Depends)
│   ├── models/
│   │   ├── base.py            ← BaseAudit (campos obligatorios ORM)
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── module.py
│   │   ├── menu.py            ← Adjacency List con parent_id
│   │   ├── user_role.py       ← Pivote M:N con auditoría
│   │   ├── role_module.py
│   │   └── role_menu.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── module.py
│   │   └── menu.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── role_service.py
│   │   ├── module_service.py
│   │   └── menu_service.py
│   ├── api/
│   │   ├── router.py
│   │   └── endpoints/
│   │       ├── auth.py        ← /api/auth/*
│   │       ├── internals.py   ← /api/internals/validate-token
│   │       ├── users.py       ← /api/users/*
│   │       ├── roles.py       ← /api/roles/*
│   │       ├── modules.py     ← /api/modules/*
│   │       └── menus.py       ← /api/menus/*
│   └── db/
│       └── seed.py            ← Datos iniciales (admin user, roles base)
└── tests/
    ├── __init__.py
    ├── test_auth.py
    ├── test_users.py
    ├── test_roles.py
    └── test_menus.py
```

---

## 📂 Fase 2 — Modelos ORM (SQLAlchemy + BaseAudit)

### `models/base.py` — Auditoría Global
Todos los modelos heredan de `BaseAudit`:
```python
id                  → UUID (primary key)
estado              → Enum("ACTIVO","INACTIVO") default="ACTIVO"
fecha_creacion      → DateTime auto en INSERT (@BeforeInsert)
fecha_actualizacion → DateTime auto en UPDATE (@BeforeUpdate)
creado_por          → UUID nullable (FK users)
actualizado_por     → UUID nullable (FK users)
```
- **Soft Delete:** nunca DELETE físico → `UPDATE estado = 'INACTIVO'`
- **Global filter:** `where(estado="ACTIVO")` automático

### Modelos
| Modelo | Campos clave |
|---|---|
| `User` | email, password_hash (bcrypt), hereda BaseAudit |
| `Role` | nombre, descripcion, hereda BaseAudit |
| `Module` | nombre, hereda BaseAudit |
| `Menu` | texto, url (nullable), parent_id (nullable), hereda BaseAudit |
| `UserRole` | user_id, role_id + campos de auditoría propios |
| `RoleModule` | role_id, module_id |
| `RoleMenu` | role_id, menu_id |

---

## 📂 Fase 3 — Endpoints (según tabla del PDF)

### Auth `/api/auth/`
| Método | Endpoint | Comportamiento |
|---|---|---|
| POST | `/login` | Credenciales → TempToken + lista de roles. Rate limiting. Mensaje genérico si falla |
| POST | `/select-role` | TempToken + roleId → JWT definitivo (Least Privilege) |
| POST | `/refresh-token` | Renueva JWT. Revoca si hay reutilización |
| POST | `/logout` | Invalida tokens en BD |

### Internals `/api/internals/`
| Método | Endpoint | Comportamiento |
|---|---|---|
| POST | `/validate-token` | Endpoint privado para microservicios hijos. Devuelve solo valid/userId/roleId |

### Users, Roles, Modules, Menus
- CRUD completo según tabla del PDF
- Todos los GET filtran `estado=ACTIVO`
- DELETE siempre es Soft Delete
- Relaciones M:N en tabla pivote con auditoría propia

### Menús Recursivos
- `GET /api/menus/tree` usa CTE con `WITH RECURSIVE`
- Árbol construido según rol del JWT activo
- Validar que nuevo `parent_id` no genere ciclos

---

## 📂 Fase 4 — Seguridad Implementada

| Requisito PDF | Implementación |
|---|---|
| Hash de contraseñas robusto | `passlib[bcrypt]` con cost factor alto |
| JWT Zero Trust | `python-jose[cryptography]`, expiración corta |
| Consultas parametrizadas | Solo ORM SQLAlchemy, prohibido string interpolation |
| Secrets en variables de entorno | `pydantic-settings` + GitHub Secrets → Render |
| Mensaje genérico en login fallido | Service retorna HTTP 401 sin especificar qué falló |
| Ocultar password en response | Serialización ORM excluye `password_hash` |
| Validación Pydantic | Regex, tipos, longitudes máx, EmailStr, bleach en texto libre |

### Variables de Entorno necesarias
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
JWT_SECRET=<secreto_fuerte>
JWT_ALGORITHM=HS256
TEMP_TOKEN_EXPIRE_MINUTES=5
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 📂 Fase 5 — Pipeline CI/CD actualizado

### Estrategia de ramas
```
main  ← Producción (solo desde test)
test  ← Staging / QA
dev   ← Desarrollo activo
feature/xxx ← desde dev
```

### Workflow `pipeline-seguro.yml` — 4 Jobs

**JOB 1 — SAST ML Gatekeeper** *(reutilizar sin cambios)*
- `scripts/analizador_ci.py` sobre archivos `.py` del PR
- Bloquea PR si código es vulnerable → Telegram 🚨

**JOB 2 — SonarQube Community** *(NUEVO)*
```yaml
- name: SonarQube Scan
  uses: sonarsource/sonarqube-scan-action@master
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
- name: Quality Gate check
  uses: sonarsource/sonarqube-quality-gate-action@master
```
- Notificación a Telegram con resultado del Quality Gate

**JOB 3 — Pytest**
- `pytest backend/tests/` con las nuevas pruebas de auth
- Notificación a Telegram

**JOB 4 — Deploy Render**
- Merge automático `test → main`
- Trigger webhook Render
- Notificación final a Telegram

### GitHub Secrets requeridos
```
TELEGRAM_TOKEN
TELEGRAM_CHAT_ID
RENDER_DEPLOY_HOOK_URL
SONAR_TOKEN           ← NUEVO
SONAR_HOST_URL        ← NUEVO (URL servidor SonarQube)
```

---

## 📂 Fase 6 — Tests (patrón heredado + ampliado)

```
test_auth.py
  ├── test_login_exitoso()
  ├── test_login_mensaje_generico_si_falla()
  ├── test_select_role_genera_jwt()
  ├── test_jwt_expirado_es_rechazado()
  └── test_refresh_token_revocacion_si_reutilizacion()

test_users.py
  ├── test_crear_usuario_exitoso()
  ├── test_pydantic_rechaza_password_corto()
  ├── test_soft_delete_cambia_estado()
  └── test_lista_solo_activos()

test_roles.py
  ├── test_no_eliminar_rol_con_usuarios_activos()
  └── test_asignar_rol_a_usuario()

test_menus.py
  ├── test_arbol_menu_recursivo()
  └── test_menu_padre_eliminado_oculta_hijos()
```

---

## ✅ Orden de Ejecución

| # | Tarea | Tipo |
|---|---|---|
| 1 | Eliminar archivos dominio LiveSeat | Limpieza |
| 2 | Actualizar `requirements.txt` | Modificar |
| 3 | Crear `core/` (config, database, security, dependencies) | Nuevo |
| 4 | Crear `models/` con BaseAudit y todas las entidades | Nuevo |
| 5 | Configurar Alembic + primera migración | Nuevo |
| 6 | Crear `schemas/` para auth, users, roles, modules, menus | Nuevo |
| 7 | Crear `services/` con lógica de negocio | Nuevo |
| 8 | Crear `endpoints/` con todos los routers | Nuevo |
| 9 | Actualizar `main.py` y `router.py` | Modificar |
| 10 | Crear tests en `backend/tests/` | Nuevo |
| 11 | Ajustar `Dockerfile` (entrypoint) | Modificar |
| 12 | Actualizar `pipeline-seguro.yml` (agregar SonarQube) | Modificar |
| 13 | Actualizar `README.md` | Modificar |

---

## ⚠️ Notas Importantes

> [!IMPORTANT]
> El modelo ML (`pipeline/models/*.joblib`) y el script `scripts/analizador_ci.py`
> NO se tocan en ningún momento. Son el SAST funcional del pipeline.

> [!NOTE]
> SonarQube Community requiere un servidor corriendo. Puede levantarse con Docker
> en Railway o una VM. La URL se guarda en el Secret `SONAR_HOST_URL`.

> [!WARNING]
> Las variables `DATABASE_URL`, `JWT_SECRET` y demás credenciales NUNCA van en
> el código. Solo en GitHub Secrets, inyectadas al contenedor en Render.

> [!NOTE]
> Para microservicios hijos futuros (ej. Módulo de Ventas): deben llamar a
> `POST /api/internals/validate-token` en cada petición (Zero Trust), o usar
> la clave pública del JWT para validar sin llamar al Master (validación asimétrica).
