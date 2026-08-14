import os
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, Response
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave-temporal-prototipo")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "inventario_istg"),
}

ESTADOS_VALIDOS = ["Bueno", "Regular", "Malo"]

# Campos del formulario, en el orden en que aparecen en el
# documento oficial de Constatación Física de Bienes.
CAMPOS_ITEM = [
    "ubicacion_actual", "cantidad", "codigo_istg", "codigo_senescyt",
    "tipo_bien", "descripcion_bien", "marca", "estado_bien",
    "gestor_responsable", "custodio_final", "cargo", "no_acta", "observacion",
]


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ------------------------------------------------------------------
# Autenticación y control de acceso por rol
# ------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para continuar.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def roles_permitidos(*roles):
    """Restringe una ruta a los roles indicados, ej. @roles_permitidos('admin', 'pasante')"""
    def decorador(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "usuario_id" not in session:
                flash("Debes iniciar sesión para continuar.", "error")
                return redirect(url_for("login"))
            if session.get("rol") not in roles:
                flash("No tienes permiso para realizar esta acción.", "error")
                return redirect(url_for("index"))
            return f(*args, **kwargs)
        return wrapper
    return decorador


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"].strip().lower()
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE correo=%s", (correo,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario and check_password_hash(usuario["password_hash"], password):
            session["usuario_id"] = usuario["id"]
            session["correo"] = usuario["correo"]
            session["rol"] = usuario["rol"]
            flash(f"Bienvenido/a, {usuario['correo']}.", "exito")
            return redirect(url_for("index"))

        flash("Correo o contraseña incorrectos.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "exito")
    return redirect(url_for("login"))


# ------------------------------------------------------------------
# CRUD de inventario
# ------------------------------------------------------------------

@app.route("/")
@login_required
def index():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items ORDER BY id DESC")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", items=items, rol=session.get("rol"))


def leer_datos_formulario():
    datos = {}
    for campo in CAMPOS_ITEM:
        valor = request.form.get(campo, "").strip()
        datos[campo] = valor
    return datos


@app.route("/agregar", methods=["GET", "POST"])
@roles_permitidos("admin", "pasante")
def agregar():
    if request.method == "POST":
        datos = leer_datos_formulario()

        if datos["estado_bien"] not in ESTADOS_VALIDOS:
            flash("Estado del bien no válido.", "error")
            return render_template("form.html", item=datos, estados=ESTADOS_VALIDOS)

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO items
                   (ubicacion_actual, cantidad, codigo_istg, codigo_senescyt,
                    tipo_bien, descripcion_bien, marca, estado_bien,
                    gestor_responsable, custodio_final, cargo, no_acta, observacion)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    datos["ubicacion_actual"], datos["cantidad"], datos["codigo_istg"],
                    datos["codigo_senescyt"], datos["tipo_bien"], datos["descripcion_bien"],
                    datos["marca"], datos["estado_bien"], datos["gestor_responsable"],
                    datos["custodio_final"], datos["cargo"], datos["no_acta"],
                    datos["observacion"],
                ),
            )
            conn.commit()
            flash("Ítem registrado correctamente.", "exito")
        except mysql.connector.IntegrityError:
            flash(f"Ya existe un ítem con el código {datos['codigo_istg']}.", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for("index"))

    return render_template("form.html", item=None, estados=ESTADOS_VALIDOS)


@app.route("/editar/<int:item_id>", methods=["GET", "POST"])
@roles_permitidos("admin", "pasante")
def editar(item_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        datos = leer_datos_formulario()

        if datos["estado_bien"] not in ESTADOS_VALIDOS:
            flash("Estado del bien no válido.", "error")
            cursor.close()
            conn.close()
            return render_template("form.html", item=datos, estados=ESTADOS_VALIDOS)

        cursor.execute(
            """UPDATE items SET
               ubicacion_actual=%s, cantidad=%s, codigo_istg=%s, codigo_senescyt=%s,
               tipo_bien=%s, descripcion_bien=%s, marca=%s, estado_bien=%s,
               gestor_responsable=%s, custodio_final=%s, cargo=%s, no_acta=%s,
               observacion=%s
               WHERE id=%s""",
            (
                datos["ubicacion_actual"], datos["cantidad"], datos["codigo_istg"],
                datos["codigo_senescyt"], datos["tipo_bien"], datos["descripcion_bien"],
                datos["marca"], datos["estado_bien"], datos["gestor_responsable"],
                datos["custodio_final"], datos["cargo"], datos["no_acta"],
                datos["observacion"], item_id,
            ),
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

    return render_template("form.html", item=item, estados=ESTADOS_VALIDOS)


@app.route("/eliminar/<int:item_id>", methods=["POST"])
@roles_permitidos("admin", "pasante")
def eliminar(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM items WHERE id=%s", (item_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Ítem eliminado.", "exito")
    return redirect(url_for("index"))


# ------------------------------------------------------------------
# Exportar a PDF (disponible para los 3 roles)
# ------------------------------------------------------------------

@app.route("/exportar-pdf")
@login_required
def exportar_pdf():
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import landscape, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from io import BytesIO

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items ORDER BY id")
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))

    encabezados = [
        "ID", "Ubicación", "Cant.", "Cód. ISTG", "Cód. SENESCYT", "Tipo",
        "Descripción", "Marca", "Estado", "Gestor", "Custodio", "Cargo",
        "No. Acta", "Observación",
    ]
    filas = [encabezados]
    for it in items:
        filas.append([
            it["id"], it["ubicacion_actual"], it["cantidad"], it["codigo_istg"],
            it["codigo_senescyt"], it["tipo_bien"], it["descripcion_bien"],
            it["marca"], it["estado_bien"], it["gestor_responsable"],
            it["custodio_final"], it["cargo"], it["no_acta"], it["observacion"],
        ])

    tabla = Table(filas, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    doc.build([tabla])
    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=inventario_istg.pdf"},
    )


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
