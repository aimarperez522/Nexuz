from app import create_app
from models import db
from models.usuario import Usuario

app = create_app()

with app.app_context():
    # Datos del admin inicial
    nombre = "Administrador"
    correo = "admin@tienda.com"
    password = "admin123"

    # Revisar si ya existe
    existente = Usuario.query.filter_by(correo=correo).first()
    if existente:
        print("⚠️ Ya existe un usuario con ese correo.")
    else:
        admin = Usuario(nombre=nombre, correo=correo, rol="admin")
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"✅ Usuario administrador creado: {correo} / {password}")
