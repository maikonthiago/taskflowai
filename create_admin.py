from app import app, db
from models import User

with app.app_context():
    # Verificar se já existe
    admin = User.query.filter_by(username='thiagolobo').first()
    if admin:
        print('Usuário admin já existe!')
    else:
        # Criar admin
        admin = User(
            username='thiagolobo',
            email='thiago@taskflowai.com',
            full_name='Thiago Lobo',
            is_admin=True
        )
        admin.set_password('#Wolf@1902')
        
        db.session.add(admin)
        db.session.commit()
        
        print('✅ Usuário admin criado com sucesso!')
        print('Username: thiagolobo')
        print('Password: #Wolf@1902')
