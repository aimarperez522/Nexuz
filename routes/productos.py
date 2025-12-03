from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
from werkzeug.utils import secure_filename
from models.producto import db, Producto

productos_bp = Blueprint("productos", __name__)

# 📁 Carpeta donde se guardarán las imágenes
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# Función auxiliar para validar extensiones
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------------------------------------------
# Listar productos (filtro por categoría)
# ------------------------------------------------------
@productos_bp.route("/productos")
def listar_productos():
    categoria = request.args.get("categoria")

    if categoria:
        productos = Producto.query.filter_by(categoria=categoria).all()
    else:
        productos = Producto.query.all()

    return render_template("productos/listar.html", productos=productos, categoria=categoria)


# ------------------------------------------------------
# Crear producto (solo admin)
# ------------------------------------------------------
@productos_bp.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    if session.get("rol") != "admin":
        flash("Acceso restringido", "danger")
        return redirect(url_for("productos.listar_productos"))

    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = float(request.form["precio"])
        stock = int(request.form["stock"])
        categoria = request.form["categoria"]   # ← NUEVO
        imagen = None

        # 📸 Procesar archivo
        if "imagen" in request.files:
            file = request.files["imagen"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                imagen = filename

        nuevo = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            imagen=imagen,
            categoria=categoria
        )

        db.session.add(nuevo)
        db.session.commit()

        flash("Producto agregado con éxito", "success")
        return redirect(url_for("productos.listar_productos"))

    return render_template("productos/nuevo.html")


# ------------------------------------------------------
# Editar producto
# ------------------------------------------------------
@productos_bp.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)

    if session.get("rol") != "admin":
        flash("Acceso restringido", "danger")
        return redirect(url_for("productos.listar_productos"))

    if request.method == "POST":
        producto.nombre = request.form["nombre"]
        producto.descripcion = request.form["descripcion"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"])
        producto.categoria = request.form["categoria"]

        # Imagen nueva opcional
        if "imagen" in request.files:
            file = request.files["imagen"]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                producto.imagen = filename

        db.session.commit()
        flash("Producto actualizado correctamente", "info")
        return redirect(url_for("productos.listar_productos"))

    return render_template("productos/editar.html", producto=producto)


# ------------------------------------------------------
# Eliminar producto
# ------------------------------------------------------
@productos_bp.route("/productos/eliminar/<int:id>")
def eliminar_producto(id):
    if session.get("rol") != "admin":
        flash("Acceso restringido", "danger")
        return redirect(url_for("productos.listar_productos"))

    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado", "warning")
    return redirect(url_for("productos.listar_productos"))
