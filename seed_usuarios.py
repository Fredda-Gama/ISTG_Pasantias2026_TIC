"""
Script para crear usuarios del sistema (admin, pasante, lectura).
Se ejecuta manualmente, una vez, para dar de alta cada usuario.

Uso:
    python seed_usuarios.py

Sigue las instrucciones en pantalla. Las contraseñas se guardan
siempre como hash (nunca en texto plano).
"""
import os
import getpass

import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "inventario_istg"),
}

DOMINIO_ADMIN = "@istg.edu.ec"


def crear_usuario():
    print("\n--- Crear nuevo usuario ---")
    print("Roles disponibles: admin, pasante, lectura")
    rol = input("Rol: ").strip().lower()

    if rol not in ("admin", "pasante", "lectura"):
        print("Rol no válido. Debe ser: admin, pasante o lectura.")
        return

    correo = input("Correo: ").strip().lower()

    if rol == "admin" and not correo.endswith(DOMINIO_ADMIN):
        print(f"Error: el rol admin requiere un correo terminado en {DOMINIO_ADMIN}")
        return

    password = getpass.getpass("Contraseña: ")
    password_confirm = getpass.getpass("Confirmar contraseña: ")

    if password != password_confirm:
        print("Las contraseñas no coinciden.")
        return

    password_hash = generate_password_hash(password)

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO usuarios (correo, password_hash, rol) VALUES (%s, %s, %s)",
            (correo, password_hash, rol),
        )
        conn.commit()
        print(f"Usuario '{correo}' creado con rol '{rol}'.")
    except mysql.connector.IntegrityError:
        print(f"Ya existe un usuario con el correo {correo}.")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    while True:
        crear_usuario()
        otro = input("\n¿Crear otro usuario? (s/n): ").strip().lower()
        if otro != "s":
            break
    print("Listo.")
