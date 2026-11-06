"use strict";

// URL base de la API definida en config.js.
// Local: "/api" (Nginx reenvía al backend). Netlify: URL pública del backend en Render.
const API_BASE_URL = ((window.APP_CONFIG && window.APP_CONFIG.apiBaseUrl) || "/api").replace(/\/+$/, "");

// Busca los elementos de index.html que se actualizarán con la respuesta de la API.
const mensaje = document.querySelector("#mensaje");
const estado = document.querySelector("#estado");
const actualizar = document.querySelector("#actualizar");
const provocarError = document.querySelector("#provocar-error");

async function cargarBienvenida() {
  estado.textContent = "Consultando el usuario en MySQL… (en Render gratis, la primera vez puede tardar ~1 minuto)";
  try {
    // El usuario 1 es el registro de ejemplo creado por database/init.sql.
    const respuesta = await fetch(`${API_BASE_URL}/usuarios/1`, { cache: "no-store" });
    if (!respuesta.ok) {
      // Convierte un estado HTTP de error en un mensaje legible para la interfaz.
      throw new Error(`La API respondió con estado ${respuesta.status}`);
    }

    // FastAPI entrega JSON; se extrae el nombre y se actualiza el contenido de la página.
    const usuario = await respuesta.json();
    mensaje.textContent = `Bienvenido, ${usuario.nombre}`;
    estado.textContent = `Nombre obtenido de MySQL (usuario #${usuario.id}).`;
  } catch (error) {
    // Informa si falló la solicitud, el backend o la consulta de base de datos.
    mensaje.textContent = "No se pudo cargar la bienvenida";
    estado.textContent = `${error.message}. Comprobá que los servicios estén activos.`;
  }
}

async function provocarErrorDePrueba() {
  estado.textContent = "Llamando a /error-prueba…";
  try {
    const respuesta = await fetch(`${API_BASE_URL}/error-prueba`, { cache: "no-store" });
    estado.textContent = `La API respondió con estado ${respuesta.status}. Revisá el dashboard de Sentry.`;
  } catch {
    // Un 500 de FastAPI no lleva cabeceras CORS, así que desde otro dominio (Netlify)
    // el navegador lo informa como error de red. Igual el error llegó a Sentry.
    estado.textContent = "El backend falló a propósito (HTTP 500). Revisá el dashboard de Sentry.";
  }
}

// El botón repite la consulta para mostrar cambios hechos directamente en MySQL.
actualizar.addEventListener("click", cargarBienvenida);
// Actividad 7: provoca una excepción no controlada en el backend.
provocarError.addEventListener("click", provocarErrorDePrueba);

// Solicita automáticamente el usuario al abrir la página.
cargarBienvenida();
