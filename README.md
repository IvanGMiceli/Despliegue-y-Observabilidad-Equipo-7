# Actividad 2 - Aplicación Full-Stack con Docker

> **Documentación relacionada**
> - [Qué es Docker y comandos principales](docs/actividad-2-docker.md) (Actividad 2)
> - [Despliegue en la nube y observabilidad con Sentry](docs/actividad-7-despliegue.md) (Actividad 7)
> - [URLs públicas de la aplicación](DESPLIEGUE.md) (entrega de la Actividad 7)

Este proyecto muestra una aplicación web sencilla compuesta por tres servicios: un frontend servido por Nginx, una API creada con FastAPI y una base de datos MySQL. Docker Compose construye y ejecuta los servicios, los conecta en una red privada y conserva los datos de MySQL en un volumen.

## Requisitos

- Docker Desktop instalado y abierto. En Windows, asegurate de que el motor de Docker esté iniciado.
- Git, si vas a clonar el repositorio.
- Una terminal (PowerShell, Windows Terminal o Git Bash).

No necesitás instalar Python, MySQL, Nginx ni Node.js en Windows. Se ejecutan o se sirven desde sus contenedores. El frontend usa HTML, CSS y JavaScript sin un paso de compilación con npm.

## Descargar o preparar el proyecto

Si todavía no tenés el proyecto, cloná el repositorio y entrá a su carpeta raíz, donde está `docker-compose.yml`:

```bash
git clone <URL_DEL_REPOSITORIO>
cd Docker
```

Si ya tenés la carpeta del proyecto, abrí una terminal en esa carpeta. En PowerShell podés comprobarlo con `Get-ChildItem`; deben aparecer `docker-compose.yml`, `backend`, `frontend` y `database`.

Copiá la plantilla de variables para crear tu archivo local `.env`:

PowerShell:

```powershell
Copy-Item .env.example .env
```

Git Bash:

```bash
cp .env.example .env
```

El archivo `.env.example` trae credenciales simples para la demostración. Podés conservarlas para ejecutar el ejemplo local o cambiarlas en `.env`. No compartas ni publiques el `.env`; el repositorio lo excluye mediante `.gitignore`. Si no creás `.env`, Compose puede usar los valores de demostración predeterminados definidos en `docker-compose.yml`.

## Iniciar toda la aplicación

Desde la carpeta raíz, con Docker Desktop iniciado, ejecutá este único comando:

```bash
docker compose up --build
```

Compose descarga las imágenes que falten, construye las imágenes del backend y frontend, crea la red y el volumen, y arranca los tres servicios. La primera ejecución puede tardar porque descarga imágenes e instala las dependencias de Python. Dejá esta terminal abierta: en este modo muestra los registros de los servicios.

Cuando MySQL termine su comprobación de salud, el backend podrá conectarse. En otra terminal, desde la misma carpeta, podés revisar el estado:

```bash
docker compose ps
```

Esperá a que los servicios aparezcan activos y MySQL figure como `healthy`. Después abrí:

- Aplicación web: <http://localhost:3000>
- Documentación de FastAPI: <http://localhost:8000/docs>
- Endpoint del usuario de ejemplo: <http://localhost:8000/usuarios/1>

Para ejecutar los servicios en segundo plano y recuperar el uso de la terminal, podés iniciar con:

```bash
docker compose up --build -d
```

En ese caso, consultá el estado con `docker compose ps` y los registros con `docker compose logs -f`. Para salir de los registros sin detener los servicios, presioná `Ctrl+C` en esa terminal de logs.

## Cómo funciona la aplicación

1. El navegador abre `localhost:3000` y Nginx entrega los archivos HTML, CSS y JavaScript.
2. El JavaScript solicita `/api/usuarios/1` mediante `fetch()`.
3. Nginx reenvía esa solicitud al servicio `backend` dentro de la red de Docker.
4. FastAPI consulta MySQL y devuelve los datos del usuario en formato JSON.
5. El navegador muestra el nombre recibido, por ejemplo, “Bienvenido, Kevin”.

MySQL no publica su puerto al equipo anfitrión; los otros servicios se conectan a él por la red privada de Compose. Para entrar a MySQL usá el comando indicado abajo.

## Consultar y modificar los datos

Con los servicios activos, abrí una segunda terminal en la carpeta raíz y ejecutá:

```bash
docker compose exec mysql mysql -uapp_user -p app_db
```

Cuando aparezca `Enter password`, escribí el valor de `MYSQL_PASSWORD` en `.env` (por defecto, `app123`) y presioná Enter. Al escribir, la contraseña no se muestra en pantalla. Si no configuraste `.env`, usá el valor predeterminado de `docker-compose.yml`.

Dentro del cliente MySQL ejecutá estas consultas, una por vez:

```sql
SHOW TABLES;
SELECT id, nombre, email FROM usuarios;
UPDATE usuarios SET nombre = 'Juan' WHERE id = 1;
SELECT id, nombre, email FROM usuarios;
```

Salí del cliente con `exit;`. Luego actualizá <http://localhost:3000> o presioná el botón “Actualizar mensaje”. La página debe mostrar “Bienvenido, Juan”.

## Persistencia de los datos

Compose monta el volumen nombrado `mysql_data` en `/var/lib/mysql`, que es donde MySQL guarda sus archivos de datos. Para detener y eliminar los contenedores y la red sin borrar la base, ejecutá:

```bash
docker compose down
```

Después podés iniciar de nuevo con `docker compose up -d` y comprobar que el nombre actualizado sigue en la página. El volumen conserva los datos entre recreaciones de los contenedores.

**No uses `docker compose down -v` si querés conservar los datos.** La opción `-v` también elimina el volumen y borra la base persistida. El script `database/init.sql` se ejecuta automáticamente solo cuando MySQL inicializa un volumen vacío; modificar el archivo después no cambia una base ya inicializada.

## Estructura del proyecto

```text
Docker/
├── .env                      # Variables locales; no se publica
├── .env.example              # Plantilla de variables necesaria para configurar el entorno
├── .gitignore                # Excluye secretos y archivos temporales
├── docker-compose.yml        # Servicios, red, volumen, puertos y healthcheck
├── README.md                 # Esta guía de instalación y uso
├── DESPLIEGUE.md             # Actividad 7: URLs públicas y credenciales de prueba
├── render.yaml               # Actividad 7: backend en Render (auto-deploy desde main)
├── netlify.toml              # Actividad 7: frontend estático en Netlify
├── docs/
│   ├── actividad-2-docker.md     # Qué es Docker y sus comandos principales
│   └── actividad-7-despliegue.md # CD, PaaS, observabilidad y paso a paso del despliegue
├── database/
│   └── init.sql              # Crea usuarios y agrega el registro inicial
├── backend/
│   ├── Dockerfile            # Construye la imagen de FastAPI
│   ├── requirements.txt      # Dependencias de Python
│   └── app/
│       ├── __init__.py
│       ├── database.py       # Configura la conexión SQLAlchemy a MySQL
│       ├── main.py           # Rutas de la API (incluye /error-prueba para Sentry)
│       ├── models.py         # Modelo de la tabla usuarios
│       └── observability.py  # Inicialización de Sentry (Actividad 7)
└── frontend/
    ├── Dockerfile            # Construye la imagen de Nginx
    ├── nginx.conf            # Sirve la web y reenvía /api al backend
    └── public/
        ├── app.js            # Solicita el usuario y muestra la bienvenida
        ├── config.js         # URL de la API (local: /api; Netlify: URL de Render)
        ├── index.html        # Estructura de la página
        └── style.css         # Estilos de la página
```

## Variables de entorno

Las variables se configuran en `.env` y Compose las usa para crear la base y conectar el backend.

| Variable | Valor de demostración | Uso |
| --- | --- | --- |
| `MYSQL_ROOT_PASSWORD` | `root123` | Contraseña administrativa de MySQL y healthcheck. |
| `MYSQL_DATABASE` | `app_db` | Nombre de la base que inicializa MySQL. |
| `MYSQL_USER` | `app_user` | Usuario de aplicación creado en MySQL. |
| `MYSQL_PASSWORD` | `app123` | Contraseña del usuario de aplicación. |
| `SENTRY_DSN` | *(vacío)* | Opcional. DSN de Sentry; vacío = Sentry desactivado. |
| `SENTRY_ENVIRONMENT` | `local` | Nombre del entorno que se ve en Sentry. |

En la nube (Actividad 7) el backend usa además `DATABASE_URL`, `DB_SSL`, `DB_SSL_CA` y `CORS_ORIGINS`, y Netlify usa `API_BASE_URL`. Ver [docs/actividad-7-despliegue.md](docs/actividad-7-despliegue.md).

El backend recibe `DATABASE_URL` desde Compose. Su host es `mysql`, el nombre del servicio dentro de la red; no lo cambies por `localhost` desde el contenedor.

## Archivos de configuración principales

- `docker-compose.yml`: declara los servicios `mysql`, `backend` y `frontend`; sus puertos, variables, red, volumen y dependencias. El backend espera a que MySQL esté saludable antes de iniciar.
- `backend/Dockerfile`: usa `python:3.11-slim`, instala `backend/requirements.txt`, copia el código de la API y arranca Uvicorn en el puerto 8000.
- `backend/requirements.txt`: enumera los paquetes que Docker instala durante el build, incluidos FastAPI, Uvicorn, SQLAlchemy, PyMySQL, Pydantic y `cryptography`.

`cryptography` es una dependencia de apoyo que PyMySQL requiere para ciertos metodos de autenticacion de MySQL, como `caching_sha2_password` o `sha256_password`, cuando se necesita el intercambio criptografico completo. La aplicacion no la importa directamente: el `RUN pip install -r requirements.txt` del Dockerfile la instala. Su version no esta fijada en este proyecto.
- `frontend/Dockerfile`: usa Nginx Alpine y copia la web y su configuración al contenedor.
- `frontend/nginx.conf`: sirve la página y reenvía las direcciones que empiezan por `/api/` al backend.
- `.env.example`: muestra las variables que debe preparar cada persona al clonar el proyecto.

## Comandos útiles

| Comando | Función |
| --- | --- |
| `docker compose up --build` | Construye las imágenes necesarias y ejecuta los servicios mostrando sus registros. |
| `docker compose up --build -d` | Construye y ejecuta los servicios en segundo plano. |
| `docker compose ps` | Muestra el estado de los servicios del proyecto. |
| `docker compose logs -f` | Sigue los registros de todos los servicios. |
| `docker compose logs -f backend` | Sigue los registros del backend. |
| `docker compose exec mysql mysql -uapp_user -p app_db` | Abre el cliente MySQL dentro del contenedor activo. |
| `docker compose down` | Detiene y elimina los contenedores y la red; conserva el volumen. |
| `docker compose down -v` | También elimina los volúmenes y los datos persistidos. |

## Problemas frecuentes

- **Docker no conecta con el motor:** abrí Docker Desktop, esperá a que termine de iniciar y repetí el comando.
- **El puerto 3000 u 8000 está ocupado:** cerrá la aplicación que lo usa o cambiá el puerto del lado izquierdo de `3000:80` o `8000:8000` en `docker-compose.yml`.
- **La web no carga los datos:** ejecutá `docker compose ps` y `docker compose logs -f backend mysql` para revisar el estado y los errores.
- **Cambiaste Python o `requirements.txt`:** reconstruí el backend con `docker compose up --build -d backend`.
- **Cambiaste HTML, CSS, JavaScript o Nginx:** reconstruí el frontend con `docker compose up --build -d frontend` y recargá la página.
- **Cambiaste las credenciales de MySQL luego de crear la base:** MySQL conserva las credenciales iniciales en el volumen existente. Para un entorno de demostración que se pueda reiniciar desde cero, `docker compose down -v` elimina ese volumen y sus datos; usalo solo si aceptás perder la información guardada.

## Cierre

Para detener el proyecto sin eliminar los datos de MySQL, ejecutá:

```bash
docker compose down
```


