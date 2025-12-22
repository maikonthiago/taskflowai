"""
Script para inicializar o banco de dados com dados de exemplo
"""
from backend.app import app, db
from backend.models import User, Workspace, Project
from backend.models_finance import Plan
from datetime import datetime

def init_database():
    with app.app_context():
        # Criar todas as tabelas
        print("Criando tabelas...")
        db.create_all()
        
        # Criar planos de assinatura
        print("Criando planos...")
        plans = [
            Plan(
                name='Gratuito',
                description='Para começar',
                price=0,
                currency='BRL',
                interval='month',
                features=['1 workspace', '3 projetos', '10 usuários', '1GB armazenamento'],
                is_active=True,
                max_workspaces=1,
                max_projects=3,
                max_users=10,
                max_storage_gb=1
            ),
            Plan(
                name='Básico',
                description='Para equipes pequenas',
                price=29.90,
                currency='BRL',
                interval='month',
                stripe_price_id='price_basic_monthly',
                features=['5 workspaces', '50 projetos', '50 usuários', '50GB armazenamento', 'IA básica'],
                is_active=True,
                max_workspaces=5,
                max_projects=50,
                max_users=50,
                max_storage_gb=50
            ),
            Plan(
                name='Pro',
                description='Para empresas',
                price=99.90,
                currency='BRL',
                interval='month',
                stripe_price_id='price_pro_monthly',
                features=['Workspaces ilimitados', 'Projetos ilimitados', 'Usuários ilimitados', '500GB armazenamento', 'IA avançada', 'Suporte prioritário'],
                is_active=True,
                max_workspaces=-1,
                max_projects=-1,
                max_users=-1,
                max_storage_gb=500
            )
        ]
        
        for plan in plans:
            existing = Plan.query.filter_by(name=plan.name).first()
            if not existing:
                db.session.add(plan)
        
        # Criar usuário admin
        print("Criando usuário admin...")
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@taskflowai.com',
                full_name='Administrador',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        db.session.commit()
        print("✅ Banco de dados inicializado com sucesso!")
        print("📧 Login: admin / admin123")

if __name__ == '__main__':
    init_database()
