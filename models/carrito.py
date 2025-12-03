from . import db
from datetime import datetime

class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    producto_id = db.Column(db.Integer, nullable=False)
    cantidad = db.Column(db.Integer, default=1)
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)
