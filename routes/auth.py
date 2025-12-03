from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.usuario import db, Usuario

# Definir el Blueprint
auth_bp = Blueprint("auth", __name__)

# ------------------------------------------------------
# RUTA: Registro de usuario
# ------------------------------------------------------
@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]

        # Verificar si ya existe el usuario
        if Usuario.query.filter_by(correo=correo).first():
            flash("El correo ya está registrado", "danger")
            return redirect(url_for("auth.registro"))

        # Crear nuevo usuario
        nuevo = Usuario(nombre=nombre, correo=correo)
        nuevo.set_password(password)
        db.session.add(nuevo)
        db.session.commit()

        flash("Usuario registrado con éxito", "success")
        return redirect(url_for("auth.login"))

    return render_template("registro.html")


# ------------------------------------------------------
# RUTA: Inicio de sesión
# ------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and usuario.check_password(password):
            session["usuario_id"] = usuario.id
            session["usuario_nombre"] = usuario.nombre
            session["rol"] = usuario.rol  # asegúrate de que el modelo Usuario tenga este campo
            flash(f"Bienvenido {usuario.nombre}", "success")
            return redirect(url_for("index"))
        else:
            flash("Credenciales incorrectas", "danger")

    return render_template("login.html")


# ------------------------------------------------------
# RUTA: Cerrar sesión
# ------------------------------------------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))
