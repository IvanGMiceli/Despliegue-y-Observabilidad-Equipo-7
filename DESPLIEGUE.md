# Despliegue y Observabilidad – Equipo #X

## URLs públicas

| Componente | Plataforma | URL |
| --- | --- | --- |
| Frontend | Netlify | https://COMPLETAR.netlify.app |
| Backend (API) | Render | https://COMPLETAR.onrender.com |
| Health check | Render | https://COMPLETAR.onrender.com/health |
| Endpoint de ejemplo | Render | https://COMPLETAR.onrender.com/usuarios/1 |
| Documentación de la API | Render | https://COMPLETAR.onrender.com/docs |
| Error de prueba (Sentry) | Render | https://COMPLETAR.onrender.com/error-prueba |
| Repositorio | GitHub | https://github.com/COMPLETAR |

## Credenciales de prueba

La aplicación no tiene login: no se necesitan credenciales para usarla.

Las credenciales de MySQL (Aiven) y el DSN de Sentry son secretos. Se cargan como variables de entorno en Render y **no se publican**.

## Notas

- El backend usa el plan gratuito de Render: si estuvo inactivo, la primera solicitud puede tardar alrededor de 1 minuto.
- El botón **Provocar error** de la página (o la URL `/error-prueba`) genera a propósito un `ZeroDivisionError`, que se ve en el dashboard de Sentry.
- Guía completa y fundamentos: [docs/actividad-7-despliegue.md](docs/actividad-7-despliegue.md).
