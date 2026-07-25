# 🐳 Guía de Despliegue con Docker — Master Gateway

Instrucciones completas para levantar el ecosistema de microservicios del **Sistema de Autenticación y Autorización Centralizado (Master Gateway)** usando Docker y Docker Compose.

---

## 📐 Arquitectura del Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network: gateway_net               │
│                                                             │
│  ┌──────────────────┐       ┌──────────────────────────┐   │
│  │   master_frontend │       │    master_api (FastAPI)   │   │
│  │   Next.js 16      │──────▶│    Puerto: 8000           │   │
│  │   Puerto: 3000    │       │    /api/auth/*            │   │
│  └──────────────────┘       │    /api/users/*           │   │
│                             │    /api/roles/*           │   │
│                             │    /api/modules/*         │   │
│                             │    /api/menus/*           │   │
│                             └──────────┬───────────────┘   │
│                                        │                    │
│                             ┌──────────▼───────────────┐   │
│                             │   master_db (PostgreSQL)  │   │
│                             │   Puerto: 5432            │   │
│                             │   Base de datos: master   │   │
│                             └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

| Contenedor         | Imagen                  | Puerto Externo | Puerto Interno |
|--------------------|-------------------------|:--------------:|:--------------:|
| `master_db`        | `postgres:16-alpine`    | `5432`         | `5432`         |
| `master_api`       | Build local (FastAPI)   | `8000`         | `8000`         |
| `master_frontend`  | Build local (Next.js)   | `3000`         | `3000`         |

---

## ✅ Pre-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo
- [Git](https://git-scm.com/) instalado
- Puertos **3000**, **5432** y **8000** libres en tu máquina

---

## 🚀 Levantando el Stack Completo

### 1. Clonar el repositorio

```bash
git clone https://github.com/cmbonifaz/Proyecto-Master-Gateway-.git
cd Proyecto-Master-Gateway-
```

### 2. Configurar las variables de entorno del backend

```bash
# Copiar el archivo de ejemplo
cp backend/.env.example backend/.env
```

Editar `backend/.env` y completar los valores:

```env
# ── Base de Datos (PostgreSQL local en Docker) ──────────────────────────────
# Para Docker Compose usa el nombre del servicio "master_db" como host
DATABASE_URL=postgresql+asyncpg://postgres:postgres@master_db:5432/master

# ── JWT ─────────────────────────────────────────────────────────────────────
# Generar con: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=CAMBIA_ESTO_POR_UN_SECRET_SEGURO_DE_64_CARACTERES
JWT_ALGORITHM=HS256

# Tiempos de expiración
TEMP_TOKEN_EXPIRE_MINUTES=5
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ── Bcrypt ───────────────────────────────────────────────────────────────────
BCRYPT_ROUNDS=12

# ── App ──────────────────────────────────────────────────────────────────────
DEBUG=False
```

> ⚠️ **NUNCA** subas el archivo `.env` al repositorio. Ya está en `.gitignore`.

### 3. Crear el `docker-compose.yml` en la raíz del proyecto

Crea el archivo `docker-compose.yml` con el siguiente contenido:

```yaml
version: "3.9"

services:

  # ── Base de Datos PostgreSQL ───────────────────────────────────────────────
  master_db:
    image: postgres:16-alpine
    container_name: master_db
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: master
    volumes:
      - pg_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - gateway_net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d master"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ── Master API (FastAPI + SQLAlchemy async) ────────────────────────────────
  master_api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: master_api
    restart: unless-stopped
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    networks:
      - gateway_net
    depends_on:
      master_db:
        condition: service_healthy
    # Aplica las migraciones y carga datos de prueba al iniciar
    command: >
      sh -c "alembic upgrade head &&
             python seed_test_data.py &&
             uvicorn app.main:app --host 0.0.0.0 --port 8000"

  # ── Frontend (Next.js) ─────────────────────────────────────────────────────
  master_frontend:
    build:
      context: ./frontend/webapp
      dockerfile: Dockerfile
    container_name: master_frontend
    restart: unless-stopped
    ports:
      - "3000:3000"
    networks:
      - gateway_net
    depends_on:
      - master_api
    environment:
      # URL interna del API (dentro de la red Docker)
      NEXT_PUBLIC_API_URL: http://localhost:8000

# ── Volúmenes persistentes ─────────────────────────────────────────────────
volumes:
  pg_data:
    name: master_gateway_pgdata

# ── Red interna ────────────────────────────────────────────────────────────
networks:
  gateway_net:
    name: gateway_net
    driver: bridge
```

### 4. Crear el `Dockerfile` del Frontend

Crea el archivo `frontend/webapp/Dockerfile`:

```dockerfile
# ── Etapa 1: Build ─────────────────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar dependencias primero (cache de capas)
COPY package.json package-lock.json ./
RUN npm ci

# Copiar código fuente y compilar
COPY . .
RUN npm run build

# ── Etapa 2: Producción (imagen mínima) ────────────────────────────────────
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Usuario no-root (seguridad)
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copiar solo los artefactos necesarios del build
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
```

> 💡 El Dockerfile del frontend usa build multi-etapa para generar una imagen mínima en producción.  
> Requiere habilitar `output: 'standalone'` en `next.config.ts` (ver paso 5).

### 5. Ajustar `next.config.ts` para modo standalone

Abre `frontend/webapp/next.config.ts` y asegúrate de que tenga:

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
};

export default nextConfig;
```

### 6. Levantar todos los servicios

```bash
# Desde la raíz del proyecto
docker compose up --build
```

Docker construirá las imágenes y levantará los 3 contenedores. La primera vez tarda ~2-5 minutos.

---

## 🌐 Acceso a los Servicios

Una vez levantado el stack:

| Servicio | URL | Descripción |
|---|---|---|
| **Frontend** | http://localhost:3000 | Interfaz web (Next.js) |
| **API REST** | http://localhost:8000 | Master Gateway API (FastAPI) |
| **Swagger UI** | http://localhost:8000/docs | Documentación interactiva de la API |
| **ReDoc** | http://localhost:8000/redoc | Documentación alternativa |
| **PostgreSQL** | `localhost:5432` | Base de datos (user: `postgres`, pass: `postgres`, db: `master`) |

---

## 👤 Cuentas de Prueba (Seed Automático)

Al iniciar el stack, el seed carga automáticamente los siguientes usuarios:

| Email | Contraseña | Rol |
|---|---|---|
| `admin@gateway.com` | `AdminPass123!` | **ADMIN** (acceso total) |
| `vendedor@gateway.com` | `Vendedor123!` | **VENDEDOR** |
| `bodega@gateway.com` | `Bodega123!` | **BODEGUERO** |
| `rrhh@gateway.com` | `RRHH123!` | **RRHH** |

---

## 🛠️ Comandos Útiles

### Verificar que los contenedores están corriendo
```bash
docker ps
```

Deberías ver algo similar a:

```
CONTAINER ID   IMAGE                    PORTS                    NAMES
xxxxxxxxxxxx   pipeline-master_api      0.0.0.0:8000->8000/tcp   master_api
xxxxxxxxxxxx   pipeline-master_front    0.0.0.0:3000->3000/tcp   master_frontend
xxxxxxxxxxxx   postgres:16-alpine       0.0.0.0:5432->5432/tcp   master_db
```

### Ver logs de un servicio específico
```bash
# Logs de la API
docker logs master_api -f

# Logs del frontend
docker logs master_frontend -f

# Logs de la base de datos
docker logs master_db -f
```

### Entrar a un contenedor
```bash
# Shell en la API
docker exec -it master_api bash

# Consola de PostgreSQL
docker exec -it master_db psql -U postgres -d master
```

### Detener el stack
```bash
docker compose down
```

### Detener y eliminar volúmenes (datos de la BD)
```bash
docker compose down -v
```

### Reconstruir un servicio específico sin afectar los demás
```bash
# Solo reconstruir la API
docker compose up --build master_api

# Solo reconstruir el frontend
docker compose up --build master_frontend
```

### Aplicar nuevas migraciones manualmente
```bash
docker exec -it master_api alembic upgrade head
```

### Ejecutar el seed manualmente
```bash
docker exec -it master_api python seed_test_data.py
```

---

## 🔍 Troubleshooting

### La API no puede conectarse a la base de datos
- Verifica que en `backend/.env`, el `DATABASE_URL` use `master_db` como host (no `localhost`).
- Espera ~10 segundos para que PostgreSQL termine de inicializar.
- Comprueba que el healthcheck de `master_db` pasó: `docker ps` debe mostrar `(healthy)`.

### El frontend no puede conectarse a la API
- Verifica que `NEXT_PUBLIC_API_URL=http://localhost:8000` esté configurado.
- Confirma que el contenedor `master_api` está corriendo: `docker ps`.

### Error de puerto ya en uso
```bash
# Ver qué proceso está usando el puerto 8000
netstat -ano | findstr :8000

# Ver qué proceso está usando el puerto 3000
netstat -ano | findstr :3000
```

### Limpiar todo y empezar desde cero
```bash
docker compose down -v
docker system prune -f
docker compose up --build
```

---

## 🏗️ Integración con Futuros Microservicios (Zero Trust)

El Master Gateway actúa como **eje centralizador** de identidad. Para integrar un microservicio hijo (ej. Módulo de Ventas):

1. El microservicio hijo valida tokens usando el endpoint interno:
   ```
   POST http://master_api:8000/api/internals/validate-token
   Authorization: Bearer <JWT>
   ```

2. Agregar el nuevo servicio al `docker-compose.yml`:
   ```yaml
   ventas_service:
     build: ./ventas
     container_name: ventas_service
     ports:
       - "3001:3001"
     networks:
       - gateway_net          # Misma red que el Master
     depends_on:
       - master_api
     environment:
       MASTER_API_URL: http://master_api:8000
   ```

3. El microservicio hijo **no tiene su propia base de usuarios** — delega toda la autenticación al Master.

---

## 🔐 Seguridad en Producción

Antes de desplegar en producción, asegúrate de:

- [ ] Cambiar `JWT_SECRET` por un valor generado con `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Cambiar `POSTGRES_PASSWORD` a una contraseña fuerte
- [ ] Configurar `DEBUG=False`
- [ ] Usar variables de entorno del proveedor cloud (no el archivo `.env`)
- [ ] Habilitar SSL/TLS en el acceso a PostgreSQL
- [ ] Limitar los puertos expuestos (solo frontend en 80/443, el resto en red interna)
