# Base pequeña de Linux con Python 3.11; Docker la obtiene si aún no está disponible.
FROM python:3.11-slim

# Los comandos siguientes se ejecutan desde /app dentro de la imagen.
WORKDIR /app

# Evita archivos .pyc y hace que los registros de Python aparezcan enseguida en Docker.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copia primero las dependencias para reutilizar esta capa si solo cambia el código.
COPY requirements.txt .
# Instala FastAPI, Uvicorn, SQLAlchemy, el driver de MySQL y sus dependencias.
RUN pip install --no-cache-dir -r requirements.txt

# Copia backend/app a /app/app dentro de la imagen para que Uvicorn importe app.main.
COPY app ./app

# Documenta el puerto interno; Compose configura su publicación hacia el equipo anfitrión.
EXPOSE 8000

# Arranca Uvicorn con el objeto FastAPI definido en app/main.py.
# 0.0.0.0 acepta conexiones de otros contenedores.
# El puerto sale de la variable PORT: las plataformas PaaS como Render la definen
# (Actividad 7); en local no existe y se usa 8000. Por eso se usa la forma "shell"
# (sh -c), que sí expande variables, y exec para que Uvicorn reciba las señales de parada.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
