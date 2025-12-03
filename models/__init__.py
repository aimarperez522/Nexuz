from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# IMPORTA tus modelos **DESPUÉS** de definir db
from .usuario import Usuario
from .producto import Producto
from .carrito import Carrito
from .pedido import Pedido
from .deseado import Deseado
