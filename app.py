"""
SGRSI - Sistema de Gestión de Recursos y Soporte de Informática
Grupo Cronos | ITI - CETP 2026

Aplicación Flask principal. Pensada para desplegar en PythonAnywhere
con Flask-MySQLdb.
"""

import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------
load_dotenv()  # Carga las variables desde el archivo .env (si existe)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave-temporal-cambiar")

app.config['MYSQL_HOST']     = os.environ.get("MYSQL_HOST")
app.config['MYSQL_USER']     = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DB']       = os.environ.get("MYSQL_DB")
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # devuelve filas como diccionarios

mysql = MySQL(app)


# ---------------------------------------------------------------------
# Decoradores de autenticación
# ---------------------------------------------------------------------
def login_requerido(f):
    """Exige que el usuario esté logueado para acceder a la ruta."""
    @wraps(f)
    def decorado(*args, **kwargs):
        if 'id_usuario' not in session:
            flash('Debés iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorado


def rol_requerido(*roles_permitidos):
    """Exige que el usuario tenga uno de los roles indicados (RF-06)."""
    def decorador(f):
        @wraps(f)
        def decorado(*args, **kwargs):
            if 'id_usuario' not in session:
                flash('Debés iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('login'))
            if session.get('rol') not in roles_permitidos:
                flash('No tenés permisos para acceder a esta sección.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorado
    return decorador


@app.context_processor
def inject_usuario():
    """Hace disponible el usuario logueado en todas las plantillas."""
    return dict(
        usuario_actual={
            'nombre': session.get('nombre'),
            'rol': session.get('rol'),
        } if 'id_usuario' in session else None
    )


# =========================================================
# AUTENTICACIÓN
# =========================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        contrasena = request.form.get('contrasena', '')

        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT u.id_usuario, u.nombre, u.apellido, u.email,
                   u.contrasena_hash, r.nombre_rol
            FROM usuarios u
            JOIN roles r ON r.id_rol = u.id_rol
            WHERE u.email = %s AND u.activo = 1
        """, (email,))
        usuario = cursor.fetchone()
        cursor.close()

        if usuario and check_password_hash(usuario['contrasena_hash'], contrasena):
            session['id_usuario'] = usuario['id_usuario']
            session['nombre'] = f"{usuario['nombre']} {usuario['apellido']}"
            session['rol'] = usuario['nombre_rol']
            flash(f"¡Bienvenido/a, {usuario['nombre']}!", 'success')
            return redirect(url_for('index'))

        flash('Email o contraseña incorrectos.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('login'))


# =========================================================
# DASHBOARD / INDEX
# =========================================================
@app.route('/')
@login_requerido
def index():
    cursor = mysql.connection.cursor()

    # Resumen de equipos por estado (RF-10)
    cursor.execute("""
        SELECT ee.nombre_estado, ee.color_hex, COUNT(*) AS cantidad
        FROM equipos e
        JOIN estados_equipo ee ON ee.id_estado_equipo = e.id_estado_equipo
        GROUP BY ee.id_estado_equipo
        ORDER BY ee.id_estado_equipo
    """)
    estados_equipos = cursor.fetchall()

    # Tickets pendientes y en proceso
    cursor.execute("""
        SELECT t.id_ticket, t.incidente, t.fecha_apertura,
               p.nombre AS prioridad, p.color_hex AS color_prioridad,
               et.nombre_estado AS estado,
               l.nombre AS laboratorio
        FROM tickets t
        JOIN prioridades p     ON p.id_prioridad = t.id_prioridad
        JOIN estados_ticket et ON et.id_estado_ticket = t.id_estado_ticket
        LEFT JOIN laboratorios l ON l.id_laboratorio = t.id_laboratorio
        WHERE et.nombre_estado != 'Resuelto'
        ORDER BY p.orden ASC, t.fecha_apertura ASC
        LIMIT 5
    """)
    tickets_activos = cursor.fetchall()

    # Solicitudes pendientes
    cursor.execute("""
        SELECT s.id_solicitud, s.descripcion, s.fecha_solicitud,
               ts.nombre AS tipo, es.nombre_estado AS estado
        FROM solicitudes s
        JOIN tipos_solicitud ts   ON ts.id_tipo_solicitud = s.id_tipo_solicitud
        JOIN estados_solicitud es ON es.id_estado_solicitud = s.id_estado_solicitud
        WHERE es.nombre_estado = 'Pendiente'
        ORDER BY s.fecha_solicitud ASC
        LIMIT 5
    """)
    solicitudes_pendientes = cursor.fetchall()

    # Contadores generales
    cursor.execute("SELECT COUNT(*) AS total FROM equipos")
    total_equipos = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COUNT(*) AS total FROM tickets t
        JOIN estados_ticket et ON et.id_estado_ticket = t.id_estado_ticket
        WHERE et.nombre_estado != 'Resuelto'
    """)
    total_tickets_abiertos = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COUNT(*) AS total FROM prestamos p
        JOIN estados_prestamo ep ON ep.id_estado_prestamo = p.id_estado_prestamo
        WHERE ep.nombre_estado = 'Activo'
    """)
    total_prestamos_activos = cursor.fetchone()['total']

    cursor.close()

    return render_template(
        'index.html',
        estados_equipos=estados_equipos,
        tickets_activos=tickets_activos,
        solicitudes_pendientes=solicitudes_pendientes,
        total_equipos=total_equipos,
        total_tickets_abiertos=total_tickets_abiertos,
        total_prestamos_activos=total_prestamos_activos,
    )


# =========================================================
# INVENTARIO (RF-02)
# =========================================================
@app.route('/inventario')
@login_requerido
def inventario():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT e.id_equipo, e.identificador, e.marca, e.modelo,
               e.observaciones,
               te.nombre_tipo AS tipo,
               ee.nombre_estado AS estado, ee.color_hex,
               l.nombre AS laboratorio
        FROM equipos e
        JOIN tipos_equipo te    ON te.id_tipo_equipo = e.id_tipo_equipo
        JOIN estados_equipo ee  ON ee.id_estado_equipo = e.id_estado_equipo
        LEFT JOIN laboratorios l ON l.id_laboratorio = e.id_laboratorio
        ORDER BY e.identificador
    """)
    equipos = cursor.fetchall()

    cursor.execute("SELECT * FROM tipos_equipo ORDER BY nombre_tipo")
    tipos_equipo = cursor.fetchall()

    cursor.execute("SELECT * FROM estados_equipo ORDER BY id_estado_equipo")
    estados_equipo = cursor.fetchall()

    cursor.execute("SELECT * FROM laboratorios WHERE activo = 1 ORDER BY nombre")
    laboratorios = cursor.fetchall()

    cursor.close()

    return render_template(
        'inventario.html',
        equipos=equipos,
        tipos_equipo=tipos_equipo,
        estados_equipo=estados_equipo,
        laboratorios=laboratorios,
    )


@app.route('/inventario/nuevo', methods=['POST'])
@login_requerido
@rol_requerido('administrador', 'tecnico')
def inventario_nuevo():
    identificador  = request.form.get('identificador', '').strip()
    id_tipo_equipo = request.form.get('id_tipo_equipo')
    marca          = request.form.get('marca', '').strip()
    modelo         = request.form.get('modelo', '').strip()
    id_estado      = request.form.get('id_estado_equipo')
    id_laboratorio = request.form.get('id_laboratorio') or None
    observaciones  = request.form.get('observaciones', '').strip()

    if not identificador or not id_tipo_equipo or not id_estado:
        flash('Completá los campos obligatorios.', 'warning')
        return redirect(url_for('inventario'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO equipos
            (identificador, id_tipo_equipo, marca, modelo,
             id_estado_equipo, id_laboratorio, observaciones)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (identificador, id_tipo_equipo, marca, modelo,
          id_estado, id_laboratorio, observaciones))
    mysql.connection.commit()
    cursor.close()

    flash(f'Equipo "{identificador}" agregado correctamente.', 'success')
    return redirect(url_for('inventario'))


@app.route('/inventario/<int:id_equipo>/estado', methods=['POST'])
@login_requerido
@rol_requerido('administrador', 'tecnico')
def inventario_actualizar_estado(id_equipo):
    """Actualiza el estado de un equipo y registra el cambio en el historial (RF-04)."""
    nuevo_estado = request.form.get('id_estado_equipo')
    descripcion  = request.form.get('descripcion', '').strip()

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE equipos SET id_estado_equipo = %s WHERE id_equipo = %s",
        (nuevo_estado, id_equipo)
    )
    cursor.execute("""
        INSERT INTO historial_equipos (id_equipo, id_usuario, id_estado_equipo, descripcion)
        VALUES (%s, %s, %s, %s)
    """, (id_equipo, session['id_usuario'], nuevo_estado, descripcion))
    mysql.connection.commit()
    cursor.close()

    flash('Estado del equipo actualizado.', 'success')
    return redirect(url_for('inventario'))


# =========================================================
# MESA DE AYUDA / TICKETS (RF-03)
# =========================================================
@app.route('/tickets')
@login_requerido
def tickets():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT t.id_ticket, t.incidente, t.descripcion,
               t.fecha_apertura, t.fecha_cierre, t.nota_resolucion,
               u.nombre AS solicitante_nombre, u.apellido AS solicitante_apellido,
               tec.nombre AS tecnico_nombre, tec.apellido AS tecnico_apellido,
               eq.identificador AS equipo,
               l.nombre AS laboratorio,
               p.nombre AS prioridad, p.color_hex AS color_prioridad,
               et.nombre_estado AS estado, t.id_estado_ticket
        FROM tickets t
        JOIN usuarios u         ON u.id_usuario = t.id_usuario
        LEFT JOIN usuarios tec  ON tec.id_usuario = t.id_tecnico
        LEFT JOIN equipos eq    ON eq.id_equipo = t.id_equipo
        LEFT JOIN laboratorios l ON l.id_laboratorio = t.id_laboratorio
        JOIN prioridades p      ON p.id_prioridad = t.id_prioridad
        JOIN estados_ticket et  ON et.id_estado_ticket = t.id_estado_ticket
        ORDER BY p.orden ASC, t.fecha_apertura DESC
    """)
    lista_tickets = cursor.fetchall()

    cursor.execute("SELECT * FROM prioridades ORDER BY orden")
    prioridades = cursor.fetchall()

    cursor.execute("SELECT * FROM estados_ticket ORDER BY id_estado_ticket")
    estados_ticket = cursor.fetchall()

    cursor.execute("SELECT id_equipo, identificador FROM equipos ORDER BY identificador")
    equipos = cursor.fetchall()

    cursor.execute("SELECT id_laboratorio, nombre FROM laboratorios WHERE activo = 1 ORDER BY nombre")
    laboratorios = cursor.fetchall()

    cursor.close()

    # Lista de incidentes comunes para el <select> (combo + opción "Otro" editable)
    incidentes_comunes = [
        'Problema de hardware', 'Problema de software', 'Faltante',
        'Equipo dañado', 'Solicitud de mantenimiento', 'Otro',
    ]

    return render_template(
        'tickets.html',
        tickets=lista_tickets,
        prioridades=prioridades,
        estados_ticket=estados_ticket,
        equipos=equipos,
        laboratorios=laboratorios,
        incidentes_comunes=incidentes_comunes,
    )


@app.route('/tickets/nuevo', methods=['POST'])
@login_requerido
def tickets_nuevo():
    incidente      = request.form.get('incidente', '').strip()
    descripcion    = request.form.get('descripcion', '').strip()
    id_prioridad   = request.form.get('id_prioridad')
    id_equipo      = request.form.get('id_equipo') or None
    id_laboratorio = request.form.get('id_laboratorio') or None

    if not incidente or not id_prioridad:
        flash('Completá el tipo de incidente y la prioridad.', 'warning')
        return redirect(url_for('tickets'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO tickets
            (id_usuario, id_equipo, id_laboratorio, incidente, descripcion, id_prioridad)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (session['id_usuario'], id_equipo, id_laboratorio, incidente, descripcion, id_prioridad))
    mysql.connection.commit()
    cursor.close()

    flash('Ticket creado correctamente.', 'success')
    return redirect(url_for('tickets'))


@app.route('/tickets/<int:id_ticket>/estado', methods=['POST'])
@login_requerido
@rol_requerido('administrador', 'tecnico')
def tickets_actualizar_estado(id_ticket):
    """El personal de soporte actualiza el estado / nota de resolución."""
    nuevo_estado    = request.form.get('id_estado_ticket')
    nota_resolucion = request.form.get('nota_resolucion', '').strip()

    cursor = mysql.connection.cursor()

    if str(nuevo_estado) == '3':  # 3 = Resuelto
        cursor.execute("""
            UPDATE tickets
            SET id_estado_ticket = %s, id_tecnico = %s,
                nota_resolucion = %s, fecha_cierre = %s
            WHERE id_ticket = %s
        """, (nuevo_estado, session['id_usuario'], nota_resolucion, datetime.now(), id_ticket))
    else:
        cursor.execute("""
            UPDATE tickets
            SET id_estado_ticket = %s, id_tecnico = %s, nota_resolucion = %s
            WHERE id_ticket = %s
        """, (nuevo_estado, session['id_usuario'], nota_resolucion, id_ticket))

    mysql.connection.commit()
    cursor.close()

    flash('Ticket actualizado.', 'success')
    return redirect(url_for('tickets'))


# =========================================================
# SOLICITUDES DE SERVICIO (RF-05)
# =========================================================
@app.route('/solicitudes')
@login_requerido
def solicitudes():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT s.id_solicitud, s.descripcion, s.fecha_solicitud, s.fecha_necesaria,
               u.nombre AS solicitante_nombre, u.apellido AS solicitante_apellido,
               ts.nombre AS tipo,
               l.nombre AS laboratorio,
               es.nombre_estado AS estado, s.id_estado_solicitud
        FROM solicitudes s
        JOIN usuarios u           ON u.id_usuario = s.id_usuario
        JOIN tipos_solicitud ts   ON ts.id_tipo_solicitud = s.id_tipo_solicitud
        LEFT JOIN laboratorios l  ON l.id_laboratorio = s.id_laboratorio
        JOIN estados_solicitud es ON es.id_estado_solicitud = s.id_estado_solicitud
        ORDER BY s.fecha_solicitud DESC
    """)
    lista_solicitudes = cursor.fetchall()

    cursor.execute("SELECT * FROM tipos_solicitud ORDER BY nombre")
    tipos_solicitud = cursor.fetchall()

    cursor.execute("SELECT * FROM estados_solicitud ORDER BY id_estado_solicitud")
    estados_solicitud = cursor.fetchall()

    cursor.execute("SELECT id_laboratorio, nombre FROM laboratorios WHERE activo = 1 ORDER BY nombre")
    laboratorios = cursor.fetchall()

    cursor.close()

    return render_template(
        'solicitudes.html',
        solicitudes=lista_solicitudes,
        tipos_solicitud=tipos_solicitud,
        estados_solicitud=estados_solicitud,
        laboratorios=laboratorios,
    )


@app.route('/solicitudes/nueva', methods=['POST'])
@login_requerido
def solicitudes_nueva():
    id_tipo_solicitud = request.form.get('id_tipo_solicitud')
    descripcion       = request.form.get('descripcion', '').strip()
    id_laboratorio    = request.form.get('id_laboratorio') or None
    fecha_necesaria   = request.form.get('fecha_necesaria') or None

    if not id_tipo_solicitud or not descripcion:
        flash('Completá el tipo de solicitud y la descripción.', 'warning')
        return redirect(url_for('solicitudes'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO solicitudes
            (id_usuario, id_tipo_solicitud, id_laboratorio, descripcion, fecha_necesaria)
        VALUES (%s, %s, %s, %s, %s)
    """, (session['id_usuario'], id_tipo_solicitud, id_laboratorio, descripcion, fecha_necesaria))
    mysql.connection.commit()
    cursor.close()

    flash('Solicitud enviada correctamente.', 'success')
    return redirect(url_for('solicitudes'))


@app.route('/solicitudes/<int:id_solicitud>/estado', methods=['POST'])
@login_requerido
@rol_requerido('administrador', 'tecnico')
def solicitudes_actualizar_estado(id_solicitud):
    nuevo_estado = request.form.get('id_estado_solicitud')

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE solicitudes SET id_estado_solicitud = %s WHERE id_solicitud = %s",
        (nuevo_estado, id_solicitud)
    )
    mysql.connection.commit()
    cursor.close()

    flash('Solicitud actualizada.', 'success')
    return redirect(url_for('solicitudes'))


# =========================================================
# PRÉSTAMOS (RF-07)
# =========================================================
@app.route('/prestamos')
@login_requerido
def prestamos():
    cursor = mysql.connection.cursor()

    cursor.execute("""
        SELECT p.id_prestamo, p.fecha_prestamo, p.fecha_devolucion_est,
               p.fecha_devolucion_real, p.observaciones,
               eq.identificador AS equipo,
               u.nombre AS usuario_nombre, u.apellido AS usuario_apellido,
               tec.nombre AS tecnico_nombre, tec.apellido AS tecnico_apellido,
               ep.nombre_estado AS estado, p.id_estado_prestamo
        FROM prestamos p
        JOIN equipos eq        ON eq.id_equipo = p.id_equipo
        JOIN usuarios u        ON u.id_usuario = p.id_usuario
        LEFT JOIN usuarios tec ON tec.id_usuario = p.id_tecnico
        JOIN estados_prestamo ep ON ep.id_estado_prestamo = p.id_estado_prestamo
        ORDER BY p.fecha_prestamo DESC
    """)
    lista_prestamos = cursor.fetchall()

    # Equipos disponibles para préstamo (estado "Correcto" y sin laboratorio asignado)
    cursor.execute("""
        SELECT e.id_equipo, e.identificador, te.nombre_tipo
        FROM equipos e
        JOIN estados_equipo ee ON ee.id_estado_equipo = e.id_estado_equipo
        JOIN tipos_equipo te   ON te.id_tipo_equipo = e.id_tipo_equipo
        WHERE ee.nombre_estado = 'Correcto'
        ORDER BY e.identificador
    """)
    equipos_disponibles = cursor.fetchall()

    cursor.execute("SELECT * FROM estados_prestamo ORDER BY id_estado_prestamo")
    estados_prestamo = cursor.fetchall()

    cursor.close()

    return render_template(
        'prestamos.html',
        prestamos=lista_prestamos,
        equipos_disponibles=equipos_disponibles,
        estados_prestamo=estados_prestamo,
    )


@app.route('/prestamos/nuevo', methods=['POST'])
@login_requerido
@rol_requerido('administrador', 'tecnico')
def prestamos_nuevo():
    id_equipo            = request.form.get('id_equipo')
    fecha_devolucion_est = request.form.get('fecha_devolucion_est') or None
    observaciones        = request.form.get('observaciones', '').strip()

    if not id_equipo:
        flash('Seleccioná un equipo para el préstamo.', 'warning')
        return redirect(url_for('prestamos'))

    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO prestamos
            (id_equipo, id_usuario, id_tecnico, fecha_devolucion_est, observaciones)
        VALUES (%s, %s, %s, %s, %s)
    """, (id_equipo, session['id_usuario'], session['id_usuario'], fecha_devolucion_est, observaciones))
    mysql.connection.commit()
    cursor.close()

    flash('Préstamo registrado correctamente.', 'success')
    return redirect(url_for('prestamos'))


@app.route('/prestamos/<int:id_prestamo>/devolver', methods=['POST'])
@login_requerido
@rol_requerido('administrador', 'tecnico')
def prestamos_devolver(id_prestamo):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE prestamos
        SET id_estado_prestamo = 2, fecha_devolucion_real = %s
        WHERE id_prestamo = %s
    """, (datetime.now(), id_prestamo))
    mysql.connection.commit()
    cursor.close()

    flash('Préstamo marcado como devuelto.', 'success')
    return redirect(url_for('prestamos'))


# =========================================================
# MÉTRICAS / DASHBOARD DE REPORTES (RF-10)
# =========================================================
@app.route('/metricas')
@login_requerido
@rol_requerido('administrador', 'tecnico')
def metricas():
    cursor = mysql.connection.cursor()

    # Equipos por estado
    cursor.execute("""
        SELECT ee.nombre_estado, ee.color_hex, COUNT(*) AS cantidad
        FROM equipos e
        JOIN estados_equipo ee ON ee.id_estado_equipo = e.id_estado_equipo
        GROUP BY ee.id_estado_equipo
        ORDER BY ee.id_estado_equipo
    """)
    equipos_por_estado = cursor.fetchall()

    # Tickets por estado
    cursor.execute("""
        SELECT et.nombre_estado, COUNT(*) AS cantidad
        FROM tickets t
        JOIN estados_ticket et ON et.id_estado_ticket = t.id_estado_ticket
        GROUP BY et.id_estado_ticket
        ORDER BY et.id_estado_ticket
    """)
    tickets_por_estado = cursor.fetchall()

    # Tickets por prioridad
    cursor.execute("""
        SELECT p.nombre, p.color_hex, COUNT(*) AS cantidad
        FROM tickets t
        JOIN prioridades p ON p.id_prioridad = t.id_prioridad
        GROUP BY p.id_prioridad
        ORDER BY p.orden
    """)
    tickets_por_prioridad = cursor.fetchall()

    # Equipos con más incidencias (top 5)
    cursor.execute("""
        SELECT eq.identificador, COUNT(*) AS cantidad_tickets
        FROM tickets t
        JOIN equipos eq ON eq.id_equipo = t.id_equipo
        GROUP BY t.id_equipo
        ORDER BY cantidad_tickets DESC
        LIMIT 5
    """)
    equipos_mas_fallados = cursor.fetchall()

    # Solicitudes por tipo
    cursor.execute("""
        SELECT ts.nombre, COUNT(*) AS cantidad
        FROM solicitudes s
        JOIN tipos_solicitud ts ON ts.id_tipo_solicitud = s.id_tipo_solicitud
        GROUP BY s.id_tipo_solicitud
        ORDER BY cantidad DESC
    """)
    solicitudes_por_tipo = cursor.fetchall()

    cursor.close()

    return render_template(
        'metricas.html',
        equipos_por_estado=equipos_por_estado,
        tickets_por_estado=tickets_por_estado,
        tickets_por_prioridad=tickets_por_prioridad,
        equipos_mas_fallados=equipos_mas_fallados,
        solicitudes_por_tipo=solicitudes_por_tipo,
    )


# =========================================================
# DIAGNÓSTICO (mantener solo en desarrollo)
# =========================================================
@app.route('/testdb')
def testdb():
    cursor = mysql.connection.cursor()
    cursor.execute("SHOW TABLES")
    data = cursor.fetchall()
    cursor.close()
    return str(data)


# =========================================================
# MAIN
# =========================================================
if __name__ == '__main__':
    app.run(debug=os.environ.get("FLASK_DEBUG", "True") == "True")
