// Configuración del frontend según el entorno.
// En local (Docker Compose) la API se pide a /api y Nginx la reenvía al backend.
// En Netlify (Actividad 7) este archivo se REEMPLAZA durante el deploy con la URL
// pública del backend en Render, tomada de la variable de entorno API_BASE_URL
// (ver netlify.toml en la raíz del repositorio).
window.APP_CONFIG = { apiBaseUrl: "/api" };
