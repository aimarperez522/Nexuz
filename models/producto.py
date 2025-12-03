from . import db

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    imagen = db.Column(db.String(200), nullable=True)
    categoria = db.Column(db.String(50), nullable=False, default="comida")
    categoria = db.Column(db.String(50), nullable=False)
