from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
import time
from models.pedido import db, Pedido
from models.carrito import Carrito
from models.producto import Producto

pedidos_bp = Blueprint("pedidos", __name__)

# ============================================================
#   CONFIRMAR PEDIDO (Carrito → Pedido Pendiente)
# ============================================================

@pedidos_bp.post("/pedidos/confirmar")
def confirmar_pedido():
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión", "danger")
        return redirect(url_for("auth.login"))

    items = Carrito.query.filter_by(usuario_id=session["usuario_id"]).all()
    if not items:
        flash("Tu carrito está vacío", "warning")
        session['carrito'] = [] 
        return redirect(url_for("carrito.ver_carrito"))
    

    # Validación de stock
    for it in items:
        prod = Producto.query.get(it.producto_id)
        if not prod:
            flash("Uno de los productos ya no existe.", "danger")
            session['carrito'] = [] 
            return redirect(url_for("carrito.ver_carrito"))

        if it.cantidad > prod.stock:
            flash(f"No queda suficiente stock de '{prod.nombre}'. Disponible: {prod.stock}", "danger")
            session['carrito'] = [] 
            return redirect(url_for("carrito.ver_carrito"))

    try:
        total = Decimal("0.00")

        # Transacción
        with db.session.begin_nested():

            productos_map = {}

            for it in items:
                prod = Producto.query.with_for_update().get(it.producto_id)
                productos_map[it.producto_id] = prod

                if it.cantidad > prod.stock:
                    raise ValueError(f"Sin stock suficiente de '{prod.nombre}'.")

            # Crear pedido pendiente
            pedido = Pedido(usuario_id=session["usuario_id"], total=0, estado="pendiente")
            db.session.add(pedido)
            db.session.flush()

            # Actualizar stock y total
            for it in items:
                prod = productos_map[it.producto_id]
                prod.stock -= it.cantidad
                db.session.add(prod)
                total += Decimal(str(prod.precio)) * Decimal(it.cantidad)

            pedido.total = total

            # Vaciar carrito
            Carrito.query.filter_by(usuario_id=session["usuario_id"]).delete()
            session['carrito'] = [] 

        db.session.commit()

        # Detectar botón presionado
        accion = request.form.get('accion')

        if accion == 'pagar':
            flash("Pedido creado. Redirigiendo a la pasarela de pago.", "info")
            return redirect(url_for("pedidos.formulario_pago", pedido_id=pedido.id))

        flash("¡Pedido confirmado! Puedes pagarlo después desde Mis Pedidos.", "success")
        return redirect(url_for("pedidos.mis_pedidos"))

    except (ValueError, SQLAlchemyError) as e:
        db.session.rollback()
        flash(str(e), "danger")
        return redirect(url_for("carrito.ver_carrito"))


# ============================================================
#   PASARELA DE PAGO MANUAL (Formulario → Procesar)
# ============================================================

@pedidos_bp.route("/pago/<int:pedido_id>", methods=["GET"])
def formulario_pago(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    
    if session.get("usuario_id") != pedido.usuario_id:
        flash("No tienes permiso para ver este pedido.", "danger")
        return redirect(url_for("index"))
        
    if pedido.estado != "pendiente":
        flash("Este pedido ya ha sido procesado.", "info")
        return redirect(url_for("pedidos.mis_pedidos"))
        
    return render_template("pedidos/pago.html", pedido=pedido)


@pedidos_bp.route("/pago/procesar/<int:pedido_id>", methods=["POST"])
def procesar_pago(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    tarjeta = request.form.get("tarjeta_numero")
    
    time.sleep(1.5)
    
    if tarjeta and len(tarjeta) >= 13:
        pedido.estado = "pagado"
        db.session.commit()
        flash("¡Pago exitoso! Tu pedido ha sido confirmado.", "success")
        return redirect(url_for("pedidos.mis_pedidos"))
    else:
        flash("Error en la tarjeta. Intenta nuevamente.", "danger")
        return redirect(url_for("pedidos.formulario_pago", pedido_id=pedido.id))


# ============================================================
#   🔥 PAGAR PENDIENTE (Botón en Mis Pedidos)
# ============================================================

@pedidos_bp.post("/pedidos/pagar_pendiente/<int:pedido_id>")
def pagar_pendiente(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)

    # Seguridad: solo el dueño puede pagar
    if session.get("usuario_id") != pedido.usuario_id:
        flash("No tienes permiso para este pedido.", "danger")
        return redirect(url_for("index"))

    # Solo permitir si está pendiente
    if pedido.estado != "pendiente":
        flash("Este pedido ya fue procesado.", "info")
        return redirect(url_for("pedidos.mis_pedidos"))

    flash("Redirigiendo a la pasarela de pago...", "info")
    return redirect(url_for("pedidos.formulario_pago", pedido_id=pedido.id))


# ============================================================
#   CONSULTAR MIS PEDIDOS
# ============================================================

@pedidos_bp.get("/pedidos/mios")
def mis_pedidos():
    if not session.get("usuario_id"):
        return redirect(url_for("auth.login"))

    pedidos = Pedido.query.filter_by(
        usuario_id=session["usuario_id"]
    ).order_by(Pedido.fecha.desc()).all()

    return render_template("pedidos/mios.html", pedidos=pedidos)


# ============================================================
#   ADMIN
# ============================================================

@pedidos_bp.get("/pedidos/admin")
def pedidos_admin():
    if session.get("rol") != "admin":
        flash("Acceso restringido", "danger")
        return redirect(url_for("index"))

    pedidos = Pedido.query.order_by(Pedido.fecha.desc()).all()
    return render_template("pedidos/admin.html", pedidos=pedidos)
