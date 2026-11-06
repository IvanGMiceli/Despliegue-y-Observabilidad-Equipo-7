"""API que recibe las solicitudes del frontend, consulta MySQL y devuelve JSON.

En local, Nginx reenvía /api/usuarios/1 a esta aplicación como /usuarios/1.
En la nube, el frontend de Netlify llama directamente a la URL pública de Render.
"""
import os

import sentry_sdk
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.observability import init_sentry

# Sentry se inicializa antes de crear la app para capturar también errores de arranque.
SENTRY_ACTIVO = init_sentry()

# Uvicorn carga este objeto mediante la referencia app.main:app.
app = FastAPI(title="Bienvenida Full-Stack", version="1.1.0")

# Orígenes que pueden llamar a la API desde el navegador.
# En local la página usa el proxy de Nginx (mismo origen); en producción se agrega
# la URL de Netlify mediante la variable CORS_ORIGINS (separadas por coma).
ORIGENES_LOCALES = ["http://localhost:3000", "http://127.0.0.1:3000"]
ORIGENES_EXTRA = [o.strip().rstrip("/") for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_LOCALES + ORIGENES_EXTRA,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health", summary="Comprueba que la API está disponible")
def health() -> dict[str, str | bool]:
    # Respuesta simple para comprobar que FastAPI está activo.
    # Render la usa como health check del servicio.
    return {"estado": "ok", "sentry": SENTRY_ACTIVO}


@app.get("/usuarios/{usuario_id}", summary="Busca un usuario por su identificador")
def obtener_usuario(usuario_id: int) -> dict[str, int | str]:
    # FastAPI toma usuario_id del segmento variable de la dirección.
    try:
        with engine.connect() as connection:
            # Busca solo las columnas que necesita el frontend.
            # El ID se envía como parámetro en lugar de concatenarse al SQL.
            row = connection.execute(
                text("SELECT id, nombre, email FROM usuarios WHERE id = :usuario_id"),
                {"usuario_id": usuario_id},
            ).mappings().first()
    except SQLAlchemyError as error:
        # Un 503 no es una excepción "no controlada", así que se reporta a Sentry a mano:
        # así una caída de la base también aparece en el dashboard.
        sentry_sdk.capture_exception(error)
        raise HTTPException(status_code=503, detail="No se pudo consultar la base de datos") from error

    if row is None:
        # Informa HTTP 404 cuando no existe un usuario con ese ID.
        raise HTTPException(status_code=404, detail="No existe ese usuario")

    # FastAPI convierte el resultado en JSON para que el navegador lo reciba.
    return dict(row)


@app.get("/error-prueba", summary="Provoca un error a propósito para verlo en Sentry")
def error_prueba() -> dict[str, float]:
    # Actividad 7: excepción NO controlada (ZeroDivisionError).
    # FastAPI responde HTTP 500 y la integración de Sentry la captura con su stack trace.
    divisor = 0
    return {"resultado": 1 / divisor}
