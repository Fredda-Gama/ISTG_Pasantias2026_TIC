-- Base de datos del prototipo de inventario
-- Ejecutar en phpMyAdmin (XAMPP) o desde la consola de MySQL

CREATE DATABASE IF NOT EXISTS inventario_istg
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE inventario_istg;

CREATE TABLE IF NOT EXISTS items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    codigo      VARCHAR(20)  NOT NULL UNIQUE,
    item        VARCHAR(150) NOT NULL,
    descripcion VARCHAR(300) NOT NULL,
    creado_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos de ejemplo (marcados como ficticios, solo para probar el prototipo)
INSERT INTO items (codigo, item, descripcion) VALUES
('IST-001', 'Silla ergonómica',      'Silla giratoria con apoyabrazos, laboratorio de sistemas'),
('IST-002', 'Escritorio',            'Escritorio individual de melamina, 1.20m'),
('IST-003', 'Proyector',             'Proyector Epson, uso compartido en aulas');
