from flask import Flask, render_template, session, request, redirect, url_for, flash
import pymysql
import config
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'clave_super_secreta_para_el_proyecto'  # Cámbiala

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection():
    return pymysql.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=config.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )

# Decorador para roles
def requiere_rol(roles_permitidos):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'rol' not in session or session['rol'] not in roles_permitidos:
                flash('No tienes permisos para acceder a esta página', 'danger')
                return redirect(url_for('listar_items'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ============================================================
# RUTAS PRINCIPALES
# ============================================================

@app.route('/')
def inicio():
    return "¡Hola! La aplicación está corriendo."

# Listar bienes (todos los roles)
@app.route('/items')
@requiere_rol(['admin', 'pasante', 'lectura'])
def listar_items():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM items ORDER BY id DESC")
            items = cursor.fetchall()
    finally:
        conn.close()
    return render_template('items.html', items=items)

# ============================================================
# RUTAS CRUD
# ============================================================

# Formulario para nuevo bien (GET)
@app.route('/nuevo', methods=['GET'])
@requiere_rol(['admin', 'pasante'])
def nuevo_bien_form():
    return render_template('nuevo.html')

# Procesar creación (POST) - Ruta separada para evitar conflictos
@app.route('/guardar', methods=['POST'])
@requiere_rol(['admin', 'pasante'])
def guardar_bien():
    data = (
        request.form['ubicacion_actual'],
        int(request.form['cantidad']),
        request.form['codigo_istg'],
        request.form['codigo_senescyt'],
        request.form['tipo_bien'],
        request.form['descripcion_bien'],
        request.form['marca'],
        request.form['estado_bien'],
        request.form['gestor_responsable'],
        request.form['custodio_final'],
        request.form['cargo'],
        request.form['no_acta'],
        request.form['observacion']
    )
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO items 
            (ubicacion_actual, cantidad, codigo_istg, codigo_senescyt, tipo_bien, 
             descripcion_bien, marca, estado_bien, gestor_responsable, custodio_final, 
             cargo, no_acta, observacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, data)
            conn.commit()
            flash('✅ Bien agregado exitosamente', 'success')
    except Exception as e:
        flash(f'❌ Error al agregar: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('listar_items'))

# Formulario para editar (GET)
@app.route('/editar/<int:id>', methods=['GET'])
@requiere_rol(['admin', 'pasante'])
def editar_bien_form(id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM items WHERE id = %s", (id,))
        item = cursor.fetchone()
    conn.close()
    if not item:
        flash('❌ Bien no encontrado', 'error')
        return redirect(url_for('listar_items'))
    return render_template('nuevo.html', item=item)

# Procesar actualización (POST)
@app.route('/editar/<int:id>', methods=['POST'])
@requiere_rol(['admin', 'pasante'])
def editar_bien(id):
    data = (
        request.form['ubicacion_actual'],
        int(request.form['cantidad']),
        request.form['codigo_istg'],
        request.form['codigo_senescyt'],
        request.form['tipo_bien'],
        request.form['descripcion_bien'],
        request.form['marca'],
        request.form['estado_bien'],
        request.form['gestor_responsable'],
        request.form['custodio_final'],
        request.form['cargo'],
        request.form['no_acta'],
        request.form['observacion'],
        id
    )
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            UPDATE items SET
            ubicacion_actual=%s, cantidad=%s, codigo_istg=%s, codigo_senescyt=%s,
            tipo_bien=%s, descripcion_bien=%s, marca=%s, estado_bien=%s,
            gestor_responsable=%s, custodio_final=%s, cargo=%s, no_acta=%s,
            observacion=%s
            WHERE id=%s
            """
            cursor.execute(sql, data)
            conn.commit()
            flash('✅ Bien actualizado exitosamente', 'success')
    except Exception as e:
        flash(f'❌ Error al actualizar: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('listar_items'))

# Eliminar (solo admin)
@app.route('/eliminar/<int:id>', methods=['POST'])
@requiere_rol(['admin'])
def eliminar_bien(id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM items WHERE id = %s", (id,))
            conn.commit()
            flash('✅ Bien eliminado exitosamente', 'success')
    except Exception as e:
        flash(f'❌ Error al eliminar: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for('listar_items'))

# ============================================================
# LOGIN / LOGOUT
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        hashed = hash_password(password)
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM usuarios WHERE correo = %s AND password_hash = %s", (correo, hashed))
            user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['correo'] = user['correo']
            session['rol'] = user['rol']
            flash('✅ Inicio de sesión exitoso', 'success')
            return redirect(url_for('listar_items'))
        else:
            flash('❌ Credenciales incorrectas', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) 