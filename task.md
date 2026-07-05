# ✅ Task Tracker — Proyecto Parcial III

## Fase 0 — Limpieza del Repositorio ✅
- [x] Eliminar archivos dominio LiveSeat
  - [x] `backend/app/api/endpoints/eventos.py`
  - [x] `backend/app/api/endpoints/reservas.py`
  - [x] `backend/app/schemas/event.py`
  - [x] `backend/app/schemas/reservation.py`
  - [x] `backend/app/models/domain.py`
  - [x] `backend/app/db/repository.py`
  - [x] `backend/app/services/event_service.py`
  - [x] `backend/app/services/reservation_service.py`
  - [x] `backend/app/prueba_seguridad.py`
  - [x] `backend/backend_docs.md`
  - [x] `pdf_content.txt`
  - [x] `pdf_content_utf8.txt`
  - [x] `vulnerable.py`
  - [x] Carpetas vacías eliminadas (db/, models/, schemas/, services/)

## Fase 1 — Nueva estructura del backend ✅
- [x] Actualizar `backend/requirements.txt` (JWT, SQLAlchemy, asyncpg, bcrypt)
- [x] Crear `backend/.env.example`
- [x] Crear `backend/app/core/__init__.py`
- [x] Crear `backend/app/core/config.py`
- [x] Crear `backend/app/core/database.py`
- [x] Crear `backend/app/core/security.py`
- [x] Crear `backend/app/core/dependencies.py`
- [x] Crear directorios: models/, schemas/, services/, api/endpoints/, db/
- [x] Actualizar `backend/app/main.py`
- [x] Actualizar `backend/app/api/router.py` (con placeholders)

## Fase 2 — Modelos ORM ✅
- [x] Crear `backend/app/models/base.py` (BaseAudit + soft_delete)
- [x] Crear `backend/app/models/user.py`
- [x] Crear `backend/app/models/role.py`
- [x] Crear `backend/app/models/module.py`
- [x] Crear `backend/app/models/menu.py` (Adjacency List)
- [x] Crear `backend/app/models/user_role.py` (pivote con auditoría)
- [x] Crear `backend/app/models/role_module.py`
- [x] Crear `backend/app/models/role_menu.py`
- [x] Actualizar `backend/app/models/__init__.py`
- [x] Inicializar Alembic (`alembic init`)
- [x] Configurar `backend/alembic/env.py` (async + autogenerate)

## Fase 3 — Schemas ✅
- [x] Crear `backend/app/schemas/auth.py` (LoginRequest, TempTokenResponse, RoleSelectRequest, TokenResponse, TokenPayload)
- [x] Crear `backend/app/schemas/user.py` (Validación de contraseña fuerte + sanitización anti-XSS con bleach)
- [x] Crear `backend/app/schemas/role.py`
- [x] Crear `backend/app/schemas/module.py`
- [x] Crear `backend/app/schemas/menu.py` (Estructura recursiva MenuNode)
- [x] Actualizar `backend/app/schemas/__init__.py`

## Fase 4 — Services ✅
- [x] Crear `backend/app/services/auth_service.py` (Lógica de autenticación en dos pasos y tokens de renovación)
- [x] Crear `backend/app/services/user_service.py` (Operaciones CRUD de usuarios y hashing de contraseña)
- [x] Crear `backend/app/services/role_service.py` (CRUD de roles y asignación/remoción de roles a usuarios)
- [x] Crear `backend/app/services/module_service.py`
- [x] Crear `backend/app/services/menu_service.py` (Generación de árbol jerárquico recursivo de menús con CTE a base de datos)
- [x] Actualizar `backend/app/services/__init__.py`

## Fase 5 — Endpoints ✅
- [x] Crear `backend/app/api/endpoints/auth.py` (/api/auth/login, /api/auth/select-role, /api/auth/refresh-token)
- [x] Crear `backend/app/api/endpoints/internals.py` (/api/internals/validate-token para microservicios hijos)
- [x] Crear `backend/app/api/endpoints/users.py` (con asignación de roles a usuario)
- [x] Crear `backend/app/api/endpoints/roles.py` (CRUD de roles y prevención de borrado de ADMIN)
- [x] Crear `backend/app/api/endpoints/modules.py`
- [x] Crear `backend/app/api/endpoints/menus.py` (/api/menus/tree con rol del JWT)
- [x] Modificar `backend/app/api/router.py` (incluir e integrar routers)
- [x] Modificar `backend/app/main.py` (configurado previamente)

## Fase 6 — Tests ✅
- [x] Crear `backend/tests/conftest.py` (Manejo de base de datos aislada con rollback automático y cliente HTTP async)
- [x] Crear `backend/tests/test_auth.py` (Pruebas de flujo de login doble y control de credenciales)
- [x] Crear `backend/tests/test_users.py` (Pruebas de complejidad Shift-Left para contraseñas)
- [x] Crear `backend/tests/test_roles.py` (Validación regex de nombres de roles)
- [x] Crear `backend/tests/test_menus.py` (Verificación del árbol de menú jerárquico recursivo vía CTE)
- [x] Limpiar `backend/tests/test_main.py` (eliminado)

## Fase 7 — Infraestructura ✅
- [x] Modificar `backend/requirements.txt` (agregar aiosqlite + greenlet para tests)
- [x] Modificar `backend/Dockerfile` (python:3.11-slim + entrypoint `app.main:app`)
- [x] Modificar `.github/workflows/pipeline-seguro.yml` (4 Jobs: ML + SonarQube self-hosted + Pytest + Deploy)
- [x] Actualizar `README.md` (documentación completa del nuevo proyecto)

## ✅ PROYECTO COMPLETO — Pendientes manuales en GitHub
- [ ] Configurar Branch Protection Rules en `main` (requerir PR + CI pass)
- [ ] Configurar Branch Protection Rules en `test` (requerir PR + CI pass)
- [ ] Verificar que el self-hosted runner está ONLINE en GitHub → Settings → Actions → Runners
- [ ] Asegurarse de que SonarQube está corriendo antes de cada ejecución del pipeline

