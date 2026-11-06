-- Script ejecutado por la imagen oficial MySQL cuando inicializa un volumen vacío.
-- Compose lo monta en /docker-entrypoint-initdb.d/01-init.sql.
-- Si el volumen ya tiene datos, MySQL no vuelve a ejecutar este archivo.

-- Tabla que consulta backend/app/main.py y cuyos datos muestra frontend/public/app.js.
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE
);

-- Usuario de demostración; el frontend solicita el registro con id 1.
-- Si el correo ya existe durante la inicialización, actualiza el nombre en vez de duplicarlo.
INSERT INTO usuarios (nombre, email)
VALUES ('Kevin', 'kevin@email.com')
ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);

