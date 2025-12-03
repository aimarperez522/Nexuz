from flask import Blueprint, session, redirect, url_for, flash, render_template
from models.deseado import db, Deseado
from models.producto import Producto

deseado_bp = Blueprint("deseado", __name__)


# ➕ Agregar a la lista de deseos
@deseado_bp.route("/deseado/agregar/<int:producto_id>")
def agregar_deseado(producto_id):
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión", "danger")
        return redirect(url_for("auth.login"))

    existe = Deseado.query.filter_by(
        usuario_id=session["usuario_id"], 
        producto_id=producto_id
    ).first()

    if existe:
        flash("Este producto ya está en tu lista de deseos.", "info")
    else:
        db.session.add(Deseado(
            usuario_id=session["usuario_id"],
            producto_id=producto_id
        ))
        db.session.commit()
        flash("Producto añadido a tu lista de deseos ❤️", "success")

    return redirect(url_for("productos.listar_productos"))


# ❌ Eliminar de la lista de deseos
@deseado_bp.route("/deseado/eliminar/<int:producto_id>")
def eliminar_deseado(producto_id):
    d = Deseado.query.filter_by(
        usuario_id=session["usuario_id"],
        producto_id=producto_id
    ).first()

    if d:
        db.session.delete(d)
        db.session.commit()
        flash("Eliminado de tu lista de deseos", "warning")

    return redirect(url_for("deseado.ver_deseados"))


# 📄 Ver lista de deseos
@deseado_bp.route("/deseado")
def ver_deseados():
    if not session.get("usuario_id"):
        return redirect(url_for("auth.login"))

    ids = Deseado.query.filter_by(usuario_id=session["usuario_id"]).all()
    productos = [Producto.query.get(i.producto_id) for i in ids]

    return render_template("deseado/listar.html", productos=productos)
