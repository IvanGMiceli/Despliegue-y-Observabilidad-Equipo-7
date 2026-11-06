# Actividad 7 – Despliegue continuo (CD) y observabilidad en la nube

Se toma la aplicación de la Actividad 2 (Nginx + FastAPI + MySQL) y se publica en internet usando solo planes gratuitos.

## 1. Arquitectura de despliegue

```text
                   push a main
  GitHub (repo público) ─────────────┬──────────────────────────────┐
                                     │ auto-deploy                  │ auto-deploy
                                     ▼                              ▼
  Navegador ──HTTPS──► Netlify (frontend estático)      Render (backend FastAPI en Docker)
       │               index.html / app.js / config.js        │            │
       │                                                       │ TLS        │ errores + trazas
       └──────────── fetch() directo a la API (CORS) ─────────►│            ▼
                                                               ▼        Sentry (dashboard)
                                                    Aiven (MySQL administrado)
```

| Pieza | Local (Actividad 2) | Nube (Actividad 7) | Plan gratuito |
| --- | --- | --- | --- |
| Frontend | Contenedor Nginx | **Netlify** | Sitios estáticos sin costo, HTTPS automático |
| Backend | Contenedor FastAPI | **Render** Web Service (mismo `backend/Dockerfile`) | Free instance: se duerme tras ~15 min sin uso |
| Base de datos | Contenedor MySQL 8.0 | **Aiven for MySQL** | Plan Free (1 servicio chico, sin tarjeta) |
| Errores | — | **Sentry** | Plan Developer: 5.000 errores/mes |

**¿Por qué Aiven?** Render no ofrece MySQL gratis (solo PostgreSQL). Para no cambiar el motor de la Actividad 2, se usa un MySQL administrado gratuito. Una alternativa compatible es TiDB Cloud Serverless. Si usan otro proveedor, solo cambia `DATABASE_URL`.

**¿Por qué el frontend llama directo a Render?** En local, Nginx hace de proxy (`/api` → backend). Netlify sirve archivos estáticos, así que `config.js` toma la URL pública del backend al desplegar. Como frontend y backend quedan en dominios distintos, el backend habilita el dominio de Netlify por **CORS** (`CORS_ORIGINS`).

## 2. Conceptos teóricos

### CI vs CD

- **Integración Continua (CI):** cada cambio que se sube al repositorio se compila y se prueba automáticamente (Actividad 6: GitHub Actions corre los tests en cada pull request). Responde a la pregunta *"¿el código está sano?"*.
- **Entrega Continua (Continuous Delivery):** el código que pasa CI queda siempre listo para publicarse, pero el pase a producción lo aprueba una persona.
- **Despliegue Continuo (Continuous Deployment):** lo que llega a la rama principal se publica solo, sin intervención manual. Responde a la pregunta *"¿los usuarios ya tienen el cambio?"*.

En este proyecto, Render y Netlify vigilan la rama `main`: un `git push` dispara el build y el deploy. Render puede configurarse además para desplegar solo si los checks de CI pasaron (*Auto-Deploy: After CI Checks Pass*). Así CI funciona como *quality gate* y CD publica.

### PaaS vs IaaS

| | IaaS (ej. una VM en AWS EC2) | PaaS (ej. Render, Netlify) |
| --- | --- | --- |
| Qué te dan | Una máquina virtual vacía | Una plataforma donde subís el código o el Dockerfile |
| Qué administrás vos | SO, actualizaciones de seguridad, Docker, firewall, HTTPS/certificados, reverse proxy, reinicios, escalado | Solo el código y las variables de entorno |
| Deploy | Scripts propios (ssh, `git pull`, reiniciar servicios) | Automático al hacer push |
| Ventajas de PaaS | — | Menos tiempo de operación, HTTPS y dominio incluidos, logs y métricas integrados, rollback a un deploy anterior con un clic |
| Contras de PaaS | — | Menos control, límites del plan, dependencia del proveedor (*vendor lock-in*) |

### Los tres pilares de la observabilidad

En producción no podés poner un `print` ni un breakpoint. Los tres pilares responden a preguntas distintas:

1. **Logs:** registros de eventos con fecha y hora (*"¿qué pasó?"*). Ejemplo: los logs de Uvicorn en Render (`GET /usuarios/1 200`).
2. **Métricas:** valores numéricos en el tiempo (*"¿cuánto? ¿está empeorando?"*). Ejemplos: uso de CPU y memoria, cantidad de requests y latencia, que Render muestra en *Metrics*.
3. **Trazas (traces):** el recorrido de una solicitud a través de los componentes (*"¿dónde se demoró o se rompió?"*). Ejemplo: Sentry Performance muestra cuánto tardó cada request de FastAPI y su consulta SQL.

Son vitales porque los errores en producción ocurren con datos y cargas reales que no estaban en los tests. Sin observabilidad, el equipo se entera por los usuarios; con ella, Sentry avisa con el stack trace, el entorno, la versión y cuántas veces pasó.

## 3. Cambios hechos al proyecto de la Actividad 2

| Archivo | Cambio |
| --- | --- |
| `backend/app/observability.py` | Nuevo. Inicializa el SDK de Sentry si existe `SENTRY_DSN`. |
| `backend/app/main.py` | Activa Sentry, toma los orígenes CORS de `CORS_ORIGINS` y suma el endpoint `/error-prueba` (divide por cero). |
| `backend/app/database.py` | Conexión TLS opcional (`DB_SSL`, `DB_SSL_CA`), necesaria para MySQL en la nube. |
| `backend/Dockerfile` | Uvicorn escucha en `$PORT` (lo define Render) o en 8000 en local. |
| `backend/requirements.txt` | Agrega `sentry-sdk[fastapi]`. |
| `frontend/public/config.js` | Nuevo. Define la URL de la API: `/api` en local y la de Render en Netlify. |
| `frontend/public/app.js` / `index.html` | Usa `config.js` y agrega el botón **Provocar error**. |
| `render.yaml` | Blueprint del backend en Render (Docker, plan free, auto-deploy desde `main`). |
| `netlify.toml` | Publica `frontend/public` y genera `config.js` con la variable `API_BASE_URL`. |
| `docker-compose.yml` / `.env.example` | Variables opcionales de Sentry. Sin DSN, todo funciona igual que antes. |

`docker compose up --build` sigue funcionando exactamente igual que en la Actividad 2.

## 4. Paso a paso del despliegue

> Hacerlo en este orden: cada paso genera un dato que necesita el siguiente.

### Paso 0 – Repositorio público en GitHub

```bash
git add .
git commit -m "Actividad 7: despliegue en Render/Netlify y Sentry"
git branch -M main
git remote add origin https://github.com/USUARIO/REPO.git
git push -u origin main
```

### Paso 1 – Sentry (DSN)

1. Crear una cuenta en <https://sentry.io> (plan Developer, gratis).
2. **Create Project** → plataforma **FastAPI** → nombre `gds-backend`.
3. Copiar el **DSN** (*Settings → Projects → gds-backend → Client Keys (DSN)*). Tiene la forma `https://xxxx@oXXXX.ingest.us.sentry.io/YYYY`.

### Paso 2 – MySQL en la nube (Aiven)

1. Crear una cuenta en <https://console.aiven.io> → **Create service** → **MySQL** → plan **Free**.
2. Cuando el servicio esté en *Running*, copiar de *Overview*: host, puerto, usuario (`avnadmin`), contraseña y base (`defaultdb`). Opcional: descargar el **CA certificate** (`ca.pem`).
3. Cargar la tabla y el usuario de ejemplo con el mismo `database/init.sql`, usando el cliente MySQL de la imagen de Docker (no hace falta instalar MySQL):

   PowerShell:
   ```powershell
   Get-Content database/init.sql | docker run --rm -i mysql:8.0 mysql -h HOST -P PUERTO -u avnadmin -pCLAVE --ssl-mode=REQUIRED defaultdb
   ```
   Git Bash:
   ```bash
   docker run --rm -i mysql:8.0 mysql -h HOST -P PUERTO -u avnadmin -pCLAVE --ssl-mode=REQUIRED defaultdb < database/init.sql
   ```
4. Para entrar a la consola interactiva (y modificar registros en la demo):
   ```bash
   docker run --rm -it mysql:8.0 mysql -h HOST -P PUERTO -u avnadmin -p --ssl-mode=REQUIRED defaultdb
   ```

### Paso 3 – Backend en Render

1. Crear una cuenta en <https://render.com> e iniciar sesión con GitHub.
2. **New → Blueprint** → elegir el repositorio. Render detecta `render.yaml` y pide las variables marcadas con `sync: false`:

   | Variable | Valor |
   | --- | --- |
   | `DATABASE_URL` | `mysql+pymysql://avnadmin:CLAVE@HOST:PUERTO/defaultdb` |
   | `SENTRY_DSN` | El DSN del paso 1 |
   | `CORS_ORIGINS` | Por ahora `http://localhost:3000`; se reemplaza en el paso 5 |
   | `DB_SSL_CA` | Opcional: pegar el contenido completo de `ca.pem` |

   `DB_SSL=true` y `SENTRY_ENVIRONMENT=production` ya vienen en el blueprint.
3. Esperar el deploy y probar `https://gds-backend-XXXX.onrender.com/health` → `{"estado":"ok","sentry":true}` y `/usuarios/1`.

*Alternativa sin Blueprint:* **New → Web Service** → repo → *Language: Docker*, *Root Directory:* `backend`, *Instance type: Free*, *Health Check Path:* `/health`, y cargar las mismas variables en *Environment*.

### Paso 4 – Frontend en Netlify

1. Crear una cuenta en <https://www.netlify.com> → **Add new site → Import an existing project → GitHub** → elegir el repositorio. Netlify toma la configuración de `netlify.toml`.
2. Antes de desplegar (o luego, en *Site configuration → Environment variables*), crear `API_BASE_URL` con la URL de Render **sin barra final**, por ejemplo `https://gds-backend-XXXX.onrender.com`.
3. Desplegar (*Deploys → Trigger deploy*). La URL queda como `https://NOMBRE.netlify.app`; se puede renombrar en *Site configuration → Change site name*.

### Paso 5 – Cerrar el circuito (CORS)

En Render → servicio → *Environment*, cambiar `CORS_ORIGINS` por la URL de Netlify (ej. `https://gds-equipo-x.netlify.app`). Render redespliega solo. Abrir la URL de Netlify: debe mostrar **"Bienvenido, Kevin"**.

### Paso 6 – Probar el despliegue continuo

Hacer un cambio visible (por ejemplo, el texto de `index.html` o un campo nuevo en `/health`), `git push` a `main` y mostrar en Render y Netlify el deploy que arranca solo.

## 5. Guion sugerido para el video (25–30 min, participan todos)

| Min. | Bloque | Contenido |
| --- | --- | --- |
| 0–3 | Presentación | Equipo, objetivo de la actividad, relación con las Actividades 2 y 6 |
| 3–9 | Teoría | CI vs CD, PaaS vs IaaS, los tres pilares de la observabilidad |
| 9–12 | Herramientas | Render, Netlify, Sentry, Aiven: qué hace cada una y por qué son gratuitas |
| 12–16 | Arquitectura y código | Diagrama de la sección 1; `render.yaml`, `netlify.toml`, `observability.py`, `config.js` |
| 16–19 | Variables de entorno | Mostrar `DATABASE_URL`, `SENTRY_DSN` y `CORS_ORIGINS` en Render y `API_BASE_URL` en Netlify (ocultar las claves) |
| 19–22 | App en vivo | URL pública de Netlify y `/health` de Render; modificar un registro en MySQL (consola) y presionar *Actualizar mensaje* |
| 22–27 | Error a propósito | Botón **Provocar error** (o abrir `/error-prueba`). En Sentry: el issue `ZeroDivisionError`, stack trace, entorno `production`, cantidad de eventos (repetir 2–3 veces para que suba), y los logs del 500 en Render |
| 27–29 | CD en vivo | Push de un cambio y deploy automático |
| 29–30 | Cierre | Conclusiones |

## 6. Problemas frecuentes

- **La primera carga tarda ~1 minuto:** el plan free de Render duerme el servicio sin tráfico. Abrir `/health` unos minutos antes de grabar.
- **"Failed to fetch" en Netlify:** `CORS_ORIGINS` en Render no coincide exactamente con la URL de Netlify (https, sin barra final) o `API_BASE_URL` está mal.
- **`/usuarios/1` devuelve 503:** revisar `DATABASE_URL` y `DB_SSL`, y que el servicio de Aiven esté *Running*. El error también aparece en Sentry.
- **`/health` dice `"sentry": false`:** falta `SENTRY_DSN` en Render.
- **El build de Netlify falla:** falta la variable `API_BASE_URL` (el comando de build la exige a propósito).
