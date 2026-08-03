import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from dotenv import load_dotenv

load_dotenv()  # Carga las variables definidas en el archivo .env (NO se sube a GitHub)

app = Flask(__name__)
app.secret_key = "clave-temporal-prototipo"  # solo para mensajes flash en desarrollo

# --- Configuración de conexión a MySQL/MariaDB ---
# Las credenciales reales viven en el archivo .env de cada máquina (ver .env.example),
# así nunca quedan escritas ni subidas al código en GitHub.
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "inventario_istg"),
}


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


@app.route("/")
def index():
    """Lista todos los ítems del inventario."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items ORDER BY id DESC")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", items=items)


@app.route("/agregar", methods=["GET", "POST"])
def agregar():
    """Formulario para registrar un nuevo ítem."""
    if request.method == "POST":
        codigo = request.form["codigo"].strip()
        item = request.form["item"].strip()
        descripcion = request.form["descripcion"].strip()

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO items (codigo, item, descripcion) VALUES (%s, %s, %s)",
                (codigo, item, descripcion),
            )
            conn.commit()
            flash("Ítem registrado correctamente.", "exito")
        except mysql.connector.IntegrityError:
            flash(f"Ya existe un ítem con el código {codigo}.", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("index"))

    return render_template("form.html", item=None)


@app.route("/editar/<int:item_id>", methods=["GET", "POST"])
def editar(item_id):
    """Formulario para editar un ítem existente."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        codigo = request.form["codigo"].strip()
        item = request.form["item"].strip()
        descripcion = request.form["descripcion"].strip()

        cursor.execute(
            "UPDATE items SET codigo=%s, item=%s, descripcion=%s WHERE id=%s",
            (codigo, item, descripcion, item_id),
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Ítem actualizado correctamente.", "exito")
        return redirect(url_for("index"))

    cursor.execute("SELECT * FROM items WHERE id=%s", (item_id,))
    item = cursor.fetchone()
    cursor.close()
    conn.close()

    if item is None:
        flash("Ítem no encontrado.", "error")
        return redirect(url_for("index"))

    return render_template("form.html", item=item)


@app.route("/eliminar/<int:item_id>", methods=["POST"])
def eliminar(item_id):
    """Elimina un ítem del inventario."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=%s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Ítem eliminado.", "exito")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
