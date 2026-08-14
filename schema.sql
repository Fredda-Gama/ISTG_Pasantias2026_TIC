-- ============================================================
-- Base de datos del sistema de inventario ISTG - v2
-- Incluye: 13 campos reales del documento de Constatación Física
-- de Bienes + tabla de usuarios para login con 3 roles
-- Ejecutar en phpMyAdmin (XAMPP) o desde la consola de MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS inventario_istg
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE inventario_istg;

-- ------------------------------------------------------------
-- Tabla: items
-- Los 13 campos vienen del documento oficial "Constatación
-- Física de Bienes" del Instituto Superior Tecnológico Guayaquil.
-- Todos son obligatorios (NOT NULL), tal como se confirmó.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS items (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    ubicacion_actual     VARCHAR(150) NOT NULL,
    cantidad             INT NOT NULL DEFAULT 1,
    codigo_istg          VARCHAR(50)  NOT NULL UNIQUE,
    codigo_senescyt      VARCHAR(50)  NOT NULL,
    tipo_bien            VARCHAR(100) NOT NULL,
    descripcion_bien     VARCHAR(300) NOT NULL,
    marca                VARCHAR(100) NOT NULL,
    estado_bien          ENUM('Bueno', 'Regular', 'Malo') NOT NULL,
    gestor_responsable   VARCHAR(150) NOT NULL,
    custodio_final       VARCHAR(150) NOT NULL,
    cargo                VARCHAR(150) NOT NULL,
    no_acta              VARCHAR(50)  NOT NULL,
    observacion          VARCHAR(300) NOT NULL,
    creado_en            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Tabla: usuarios
-- Login con 3 roles: admin, pasante, lectura
-- - admin: correo obligatorio con dominio @istg.edu.ec
-- - pasante y lectura: cualquier correo
-- Las contraseñas NUNCA se guardan en texto plano, solo su hash.
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    correo        VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol           ENUM('admin', 'pasante', 'lectura') NOT NULL,
    creado_en     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Datos de ejemplo (ficticios, solo para probar el sistema)
-- ------------------------------------------------------------
INSERT INTO items (
    ubicacion_actual, cantidad, codigo_istg, codigo_senescyt, tipo_bien,
    descripcion_bien, marca, estado_bien, gestor_responsable,
    custodio_final, cargo, no_acta, observacion
) VALUES
('Bienestar Institucional', 1, 'GYE-SRP-01-00001', 'N/A', 'Silla respaldo',
 'Silla respaldo plástico, metal color negro', 'S/N', 'Bueno',
 'Bienestar Institucional', 'Custodio Ejemplo', 'Gestor de Apoyo',
 '2025-G-093', 'Ninguna'),
('Coordinación Software', 1, 'GYE-CPU-01-00001', 'QVFN3HA057054', 'CPU',
 'CPU torre', 'Adikta', 'Bueno',
 'Coordinación de Software', 'Custodio Ejemplo 2', 'Coordinador',
 '2025-G-100', 'Ninguna');

-- Nota: los usuarios (admin/pasante/lectura) se crean desde la
-- aplicación (con contraseña hasheada), no directamente aquí con
-- texto plano. Ver seed_usuarios.py una vez creado app.py.
