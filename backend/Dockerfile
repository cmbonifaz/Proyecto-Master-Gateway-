# Dockerfile optimizado para producción siguiendo Secure SDLC (Mínimo privilegio y superficie reducida)

# 1. Usamos una imagen base "slim" para reducir dependencias innecesarias del SO y minimizar la superficie de ataque.
FROM python:3.10-slim

# 2. Variables de entorno recomendadas
# Evita que Python escriba archivos .pyc en el disco
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python guarde los logs en el buffer de salida estándar (útil para logs centralizados)
ENV PYTHONUNBUFFERED=1

# 3. Establecemos el directorio de trabajo
WORKDIR /app

# 4. Copiamos solo el archivo de requerimientos primero para aprovechar la caché de capas de Docker
COPY requirements.txt .

# 5. Instalamos dependencias sin guardar el caché de pip para mantener la imagen ligera
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiamos el resto del código fuente del backend
COPY . .

# 7. SEGURIDAD: Crear y usar un usuario no-root (Mínimo Privilegio)
# Esto mitiga significativamente el daño en caso de que un atacante logre un RCE (Remote Code Execution)
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# 8. Variable de entorno requerida por el entorno dinámico de Render
# Render inyecta un puerto dinámico mediante la variable $PORT. Dejamos el 8000 como default.
ENV PORT=8000

# 9. Comando de ejecución
# Usamos el modo shell (CMD command) para que Docker evalúe e inyecte correctamente la variable $PORT 
# en los argumentos de uvicorn al momento de iniciar el contenedor.
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
