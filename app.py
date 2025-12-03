from flask import Flask, render_template
from config import Config
from models.usuario import db
from models.producto import Producto  # ✅ Importamos el modelo de productos
#from models.queja import Queja
from routes.auth import auth_bp
from routes.productos import productos_bp
from routes.carrito import carrito_bp
from routes.pedidos import pedidos_bp
from routes.deseado import deseado_bp




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar la base de datos
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Registrar blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(productos_bp)  # sin prefijo → /productos
    app.register_blueprint(carrito_bp)    # sin prefijo → /carrito
    app.register_blueprint(pedidos_bp)    # sin prefijo → /pedidos
    app.register_blueprint(deseado_bp)

    # 🏠 Ruta principal (index)
    @app.route("/")
    def index():
        # ✅ Obtener hasta 6 productos (para mostrar en portada)
        productos = Producto.query.limit(6000).all()
        return render_template("index.html", productos=productos)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
