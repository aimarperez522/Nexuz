# routes/carrito.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from models.carrito import db, Carrito
from models.producto import Producto

carrito_bp = Blueprint("carrito", __name__)

# Ver carrito
@carrito_bp.route("/carrito")
def ver_carrito():
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión", "danger")
        return redirect(url_for("auth.login"))

    items = Carrito.query.filter_by(usuario_id=session["usuario_id"]).all()
    total = sum([Producto.query.get(i.producto_id).precio * i.cantidad for i in items])
    return render_template("carrito/ver.html", items=items, total=total, Producto=Producto)

#actualizar carrito
@carrito_bp.post("/carrito/actualizar")
def actualizar_carrito():
    if not session.get("usuario_id"):
        return redirect(url_for("auth.login"))

    items = Carrito.query.filter_by(usuario_id=session["usuario_id"]).all()
    cambios = 0
    for it in items:
        req = request.form.get(f"qty_{it.id}", type=int)
        if req is None:
            continue
        if req <= 0:
            db.session.delete(it)
            cambios += 1
            continue

        prod = Producto.query.get(it.producto_id)
        if not prod:
            db.session.delete(it)
            cambios += 1
            continue

        # ✔ validación extra (recomendado)
        if req > prod.stock:
            flash(f"No puedes establecer más de {prod.stock} unidades de '{prod.nombre}'.", "danger")

        if req > prod.stock:
            it.cantidad = prod.stock
            cambios += 1
            flash(f"Ajustado '{prod.nombre}' a {prod.stock} por stock.", "info")
        else:
            it.cantidad = req
            cambios += 1

    if cambios:
        db.session.commit()
        flash("Carrito actualizado", "success")
    return redirect(url_for("carrito.ver_carrito"))

# routes/carrito.py
@carrito_bp.route("/carrito/agregar/<int:producto_id>", methods=["POST"])
def agregar_carrito(producto_id):
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión", "danger")
        return redirect(url_for("auth.login"))

    cantidad_req = request.form.get("cantidad", type=int) or 1
    if cantidad_req < 1:
        cantidad_req = 1

    prod = Producto.query.get_or_404(producto_id)
# 1. Obtener carrito actual
    carrito = session.get('carrito', [])

# 2. Agregar producto al carrito (aquí NO toco tu lógica)
    carrito.append({
     "id": prod.id,
     "cantidad": cantidad_req
    })
# O si tú usas otro formato, mantengo tu formato, solo asegúrate de agregar aquí.

# 3. Guardar carrito en sesión
    session['carrito'] = carrito
    
    

    # Si no hay stock, no permitas agregar
    if prod.stock <= 0:
        flash(f"'{prod.nombre}' está agotado.", "warning")
        return redirect(url_for("productos.listar_productos"))

    # ✔ validación preventiva
    if cantidad_req > prod.stock:
        flash(f"No puedes agregar más de {prod.stock} unidades de '{prod.nombre}'.", "danger")
        return redirect(url_for("productos.listar_productos"))

    item = Carrito.query.filter_by(usuario_id=session["usuario_id"], producto_id=producto_id).first()
    cantidad_actual = item.cantidad if item else 0
    nueva_cantidad = cantidad_actual + cantidad_req

    # Tope por inventario
    if nueva_cantidad > prod.stock:
        nueva_cantidad = prod.stock
        flash(f"Ajustado a {prod.stock} por stock disponible en '{prod.nombre}'.", "info")

    if item:
        item.cantidad = nueva_cantidad
    else:
        db.session.add(Carrito(usuario_id=session["usuario_id"], producto_id=producto_id, cantidad=nueva_cantidad))

    db.session.commit()
    flash(f"{prod.nombre} agregado al carrito", "success")
    return redirect(url_for("productos.listar_productos"))

# Eliminar producto del carrito
@carrito_bp.post("/carrito/eliminar/<int:item_id>")
def eliminar_item(item_id):
    if not session.get("usuario_id"):
        return redirect(url_for("auth.login"))

    it = Carrito.query.get_or_404(item_id)
    if it.usuario_id != session["usuario_id"]:
        flash("Operación no permitida", "danger")
        return redirect(url_for("carrito.ver_carrito"))

    db.session.delete(it)
    db.session.commit()
    flash("Producto eliminado del carrito", "warning")
    return redirect(url_for("carrito.ver_carrito"))
    
    session['carrito'] = carrito   # ← actualiza el contador



# Vaciar carrito completo
@carrito_bp.route("/carrito/vaciar")
def vaciar_carrito():
    if not session.get("usuario_id"):
        return redirect(url_for("auth.login"))

    Carrito.query.filter_by(usuario_id=session["usuario_id"]).delete()
    db.session.commit()
    flash("Carrito vaciado", "info")
    session['carrito'] = []   # ← contador vuelve a 0
    return redirect(url_for("carrito.ver_carrito"))