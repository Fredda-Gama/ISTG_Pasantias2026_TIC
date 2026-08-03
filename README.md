# Prototipo de inventario — ISTG

Prototipo funcional de sistema de inventario (código, ítem, descripción) para prácticas preprofesionales. Flask + MySQL/MariaDB.

## Requisitos

- Python 3.10+
- MySQL o MariaDB corriendo localmente (vía XAMPP o instalación independiente)

## Instalación

1. Clonar el repositorio y entrar a la carpeta del proyecto.
2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Copiar `.env.example` como `.env` y poner tus propias credenciales de la base de datos:
   ```
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=tu_password
   DB_NAME=inventario_istg
   ```
   ⚠️ El archivo `.env` es personal de cada máquina y **no se sube a GitHub** (está en `.gitignore`).
4. Ejecutar `schema.sql` en tu gestor de base de datos (phpMyAdmin, HeidiSQL, o consola) para crear la base de datos y las 3 filas de ejemplo.
5. Ejecutar la aplicación:
   ```
   python app.py
   ```
6. Abrir en el navegador: http://127.0.0.1:5000

## Estructura

- `app.py` — backend Flask con las 4 rutas del CRUD (listar, agregar, editar, eliminar)
- `schema.sql` — creación de la base de datos y datos de ejemplo
- `templates/` — plantillas HTML (base, listado, formulario)
- `.env.example` — plantilla de variables de entorno (copiar como `.env`)
- `requirements.txt` — dependencias de Python
