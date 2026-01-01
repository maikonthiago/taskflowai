from app import app, db
from models import User
import sys

def reset_password():
    print("=== RESET ADMIN PASSWORD ===")
    with app.app_context():
        # Tenta encontrar o usuário
        username = 'thiagolobo'
        user = User.query.filter_by(username=username).first()
        
        new_pass = '#Wolf@1902'
        
        if user:
            print(f"Usuário '{username}' encontrado. Atualizando senha...")
            user.set_password(new_pass)
            user.is_admin = True # Garante que é admin
        else:
            print(f"Usuário '{username}' NÃO encontrado. Criando novo...")
            user = User(
                username=username,
                email='thiago@taskflowai.com',
                full_name='Thiago Lobo',
                is_admin=True
            )
            user.set_password(new_pass)
            db.session.add(user)
            
        try:
            db.session.commit()
            print("✅ SUCESSO! Senha atualizada/criada.")
            print(f"User: {username}")
            print(f"Pass: {new_pass}")
        except Exception as e:
            print(f"❌ ERRO ao salvar no banco: {e}")
            db.session.rollback()

if __name__ == "__main__":
    reset_password()
