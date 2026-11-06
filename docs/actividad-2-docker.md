# Actividad 2 – Qué es Docker y sus comandos principales

## Qué es Docker

Docker es una plataforma para empaquetar una aplicación junto con todo lo que necesita para ejecutarse (sistema base, intérprete, librerías, configuración) en una **imagen**, y ejecutarla como un **contenedor**: un proceso aislado que comparte el kernel del sistema anfitrión.

| Concepto | Qué es | En este proyecto |
| --- | --- | --- |
| **Imagen** | Plantilla de solo lectura, construida en capas | `python:3.11-slim`, `nginx:alpine`, `mysql:8.0` |
| **Dockerfile** | Receta para construir una imagen | `backend/Dockerfile`, `frontend/Dockerfile` |
| **Contenedor** | Instancia en ejecución de una imagen | `mysql`, `backend`, `frontend` |
| **Volumen** | Almacenamiento que sobrevive al contenedor | `mysql_data` → `/var/lib/mysql` |
| **Red** | Comunicación entre contenedores por nombre | `app_network` (bridge personalizada) |
| **Registry** | Repositorio de imágenes | Docker Hub (de donde se descargan las imágenes base) |
| **Docker Compose** | Define y levanta varios contenedores juntos | `docker-compose.yml` |

### Contenedor vs máquina virtual

Una máquina virtual emula hardware y arranca un sistema operativo completo (GB de disco, minutos de arranque). Un contenedor solo aísla procesos sobre el mismo kernel: pesa MB, arranca en segundos y se pueden correr muchos en la misma máquina.

## Relevancia técnica

- **"En mi máquina funciona" deja de ser un problema:** el entorno es idéntico en la PC de cada integrante, en el servidor de CI y en producción.
- **Reproducibilidad:** el Dockerfile y el `docker-compose.yml` documentan como código cómo se arma el entorno.
- **Base de CI/CD:** el pipeline construye la imagen una vez y la misma imagen se prueba y se despliega (en la Actividad 7, Render usa el mismo `backend/Dockerfile`).
- **Microservicios:** cada servicio (web, API, base de datos) vive en su contenedor, con sus dependencias, y se escala o actualiza por separado.
- **Aislamiento:** distintos proyectos pueden usar versiones distintas de Python o MySQL sin conflictos.
- **Portabilidad:** funciona igual en Windows, Linux, macOS y en cualquier proveedor de nube.

## Comandos principales

### Imágenes

| Comando | Propósito |
| --- | --- |
| `docker pull mysql:8.0` | Descarga una imagen desde un registry |
| `docker build -t gds-backend ./backend` | Construye una imagen a partir de un Dockerfile |
| `docker images` | Lista las imágenes locales |
| `docker rmi gds-backend` | Elimina una imagen |
| `docker push usuario/gds-backend` | Sube una imagen a un registry |

### Contenedores

| Comando | Propósito |
| --- | --- |
| `docker run -d -p 8000:8000 --name api gds-backend` | Crea y arranca un contenedor (`-d` en segundo plano, `-p` publica un puerto) |
| `docker ps` / `docker ps -a` | Lista los contenedores activos / todos |
| `docker logs -f api` | Muestra (y sigue) la salida del contenedor |
| `docker exec -it api sh` | Ejecuta un comando dentro de un contenedor en marcha |
| `docker stop api` / `docker start api` | Detiene / vuelve a arrancar un contenedor |
| `docker rm api` | Elimina un contenedor detenido |
| `docker inspect api` | Muestra la configuración completa (red, IP, volúmenes, variables) |

### Redes y volúmenes

| Comando | Propósito |
| --- | --- |
| `docker network ls` | Lista las redes (aparece `docker_fullstack_network`) |
| `docker network inspect docker_fullstack_network` | Muestra qué contenedores están conectados |
| `docker volume ls` | Lista los volúmenes |
| `docker volume inspect <volumen>` | Muestra dónde se guardan los datos |

### Docker Compose

| Comando | Propósito |
| --- | --- |
| `docker compose up --build` | Construye las imágenes y levanta todos los servicios |
| `docker compose up --build -d` | Igual, en segundo plano |
| `docker compose ps` | Estado de los servicios |
| `docker compose logs -f backend` | Logs de un servicio |
| `docker compose exec mysql mysql -uapp_user -p app_db` | Consola interactiva de MySQL |
| `docker compose down` | Detiene y borra contenedores y red (conserva el volumen) |
| `docker compose down -v` | También borra el volumen con los datos |

### Limpieza

| Comando | Propósito |
| --- | --- |
| `docker system df` | Espacio usado por imágenes, contenedores y volúmenes |
| `docker system prune` | Elimina contenedores detenidos, redes sin uso e imágenes huérfanas |
