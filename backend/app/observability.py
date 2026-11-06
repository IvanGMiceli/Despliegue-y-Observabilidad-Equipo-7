"""Integración con Sentry para el seguimiento de errores en producción.

Sentry solo se activa si existe la variable SENTRY_DSN. En local (Docker Compose)
puede quedar vacía y la aplicación funciona igual, sin enviar nada.
"""
import os

import sentry_sdk


def init_sentry() -> bool:
    """Inicializa el SDK de Sentry. Devuelve True si quedó activo."""
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if not dsn:
        return False

    sentry_sdk.init(
        dsn=dsn,
        # Permite distinguir en el dashboard los errores de producción de los locales.
        environment=os.getenv("SENTRY_ENVIRONMENT", "development"),
        # Versión del código desplegado; Render expone el commit en RENDER_GIT_COMMIT.
        release=os.getenv("RENDER_GIT_COMMIT") or None,
        # Porcentaje de solicitudes que se envían como trazas de rendimiento (0.0 a 1.0).
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0")),
        # No envía datos personales (IP, cabeceras) del usuario final.
        send_default_pii=False,
    )
    # Con sentry-sdk 2.x, la integración de FastAPI/Starlette se activa sola al detectarlos.
    return True
