"""Conexión entre FastAPI y MySQL.

En local, Compose proporciona DATABASE_URL al contenedor backend y SQLAlchemy usa
PyMySQL para comunicarse con el servicio mysql dentro de la red privada de Docker.

En la nube (Actividad 7), DATABASE_URL apunta a un MySQL administrado (por ejemplo,
Aiven) que exige conexión cifrada: para eso están DB_SSL y DB_SSL_CA.
"""
import os
import ssl

from sqlalchemy import create_engine

# Compose crea esta URL con variables de .env; en Render se carga como variable de entorno.
# El valor alternativo sirve fuera de Compose si hay un host mysql accesible.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://app_user:app123@mysql:3306/app_db",
)


def _ssl_connect_args() -> dict:
    """Arma la configuración TLS para MySQL según las variables de entorno.

    - DB_SSL_CA: contenido PEM del certificado CA del proveedor -> cifrado y verificado.
    - DB_SSL=true sin CA: cifrado, pero sin verificar el certificado del servidor.
    - Ninguna: conexión sin TLS (caso de la red interna de Docker Compose).
    """
    ca_pem = os.getenv("DB_SSL_CA", "").strip()
    if ca_pem:
        return {"ssl": ssl.create_default_context(cadata=ca_pem)}

    if os.getenv("DB_SSL", "").strip().lower() in {"1", "true", "yes"}:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        return {"ssl": context}

    return {}


# El engine administra las conexiones usadas por las rutas de la API.
# pool_pre_ping comprueba una conexión antes de reutilizarla.
# pool_recycle renueva conexiones viejas que los servicios en la nube suelen cortar.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=280,
    connect_args=_ssl_connect_args(),
)
