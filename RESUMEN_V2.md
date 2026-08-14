# Inventario ISTG — v2 (login + 13 campos reales)

## Qué se hizo

1. **`schema.sql`** — reescrito con los 13 campos reales del documento
   de Constatación Física de Bienes, más una tabla `usuarios` para el
   login (correo, password_hash, rol).

2. **`app.py`** — reescrito con:
   - Login con sesión (`/login`, `/logout`)
   - 3 roles: `admin`, `pasante` (mismo permiso que admin: CRUD completo),
     `lectura` (solo consulta y exportar PDF)
   - Restricción: el rol `admin` requiere correo `@istg.edu.ec`
     (se valida en `seed_usuarios.py` al crear el usuario)
   - CRUD adaptado a los 13 campos, con `estado_bien` como lista
     desplegable (Bueno / Regular / Malo)
   - Ruta `/exportar-pdf` — genera un PDF con toda la tabla, disponible
     para los 3 roles (usa la librería `reportlab`)

3. **`templates/`** — `base.html`, `login.html`, `index.html` (13
   columnas + botones según rol), `form.html` (13 campos)

4. **`seed_usuarios.py`** — script de consola para crear usuarios con
   contraseña hasheada (nunca en texto plano), validando el dominio
   institucional para admin

5. **`requirements.txt`** y **`.env.example`** actualizados
   (se agregó `Werkzeug`, `reportlab`, y `SECRET_KEY`)

## Pendiente para cuando retomemos

- [ ] Probar todo localmente: crear la base con el nuevo `schema.sql`,
      correr `seed_usuarios.py` para crear un admin y un usuario de
      cada rol, y hacer login
- [ ] Revisar juntas los 13 campos: ¿el formulario debería tener
      ayudas visuales (placeholders) como en el documento original?
- [ ] Confirmar con el Ing. Franklin: ¿"Código SENESCYT" realmente
      debe ser obligatorio, dado que en el documento real muchas filas
      lo tienen vacío?
- [ ] Empaquetado final para instalar en la computadora del
      Tecnológico (lo que pidió al final) — todavía no se ha
      trabajado, se hace después de validar el CRUD + login
- [ ] Fase 3 (después): importar desde Excel/CSV

## Cómo lo vamos a probar cuando vuelvas

1. Ejecutar `schema.sql` en HeidiSQL o phpMyAdmin (esto reemplaza la
   tabla `items` — si quieres conservar los datos viejos, avísame
   antes de correrlo)
2. `pip install -r requirements.txt`
3. `python seed_usuarios.py` — crear al menos un usuario admin
4. `python app.py` y probar el login + CRUD completo
