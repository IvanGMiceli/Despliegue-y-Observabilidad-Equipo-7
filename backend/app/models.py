"""Modelo declarativo de la tabla usuarios.

El esquema de la base se crea en database/init.sql. La ruta actual de main.py
consulta con SQL directo; esta clase documenta el esquema en Python.
"""
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Clase base de los modelos declarativos de SQLAlchemy.
class Base(DeclarativeBase):
    pass


class Usuario(Base):
    # Debe coincidir con el nombre de tabla usado por el SQL y la API.
    __tablename__ = "usuarios"

    # Identificador único de cada registro.
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Nombre que la página presenta en el saludo.
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    # Correo obligatorio y único para cada usuario.
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

