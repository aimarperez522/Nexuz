from . import db
from datetime import datetime

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default="pendiente")  # pendiente | pagado | entregado
