# Imagen oficial de Nginx sobre Alpine, que sirve los archivos estáticos del frontend.
FROM nginx:alpine

# Copia HTML, CSS y JavaScript al directorio público predeterminado de Nginx.
COPY public/ /usr/share/nginx/html/

# Instala la configuración personalizada que también redirige /api al backend.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Puerto interno de Nginx; Compose lo publica como localhost:3000 en el equipo.
EXPOSE 80

