#!/usr/bin/env python3
"""
TaskFlowAI - Script de Inicialização
Inicializa o banco de dados e cria usuário admin
"""
import os
import sys

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def init_database():
    """Inicializa o banco de dados"""
    print("🚀 Inicializando TaskFlowAI...")
    print("=" * 50)
    
    # Configurar ambiente
    os.environ['FLASK_ENV'] = 'production'
    
    # Importar app
    from app import app, db
    
    with app.app_context():
        print("📦 Criando tabelas do banco de dados...")
        db.create_all()
        
        print("🔧 Configurando dados padrão...")
        from app import ensure_default_data
        ensure_default_data()
        
        print("✓ Banco de dados inicializado com sucesso!")
        print()


def create_admin():
    """Cria usuário administrador"""
    print("👤 Criando usuário administrador...")
    print("=" * 50)
    
    # Configurar ambiente
    os.environ['FLASK_ENV'] = 'production'
    
    # Importar app e models
    from app import app, db
    from models import User, Workspace
    
    with app.app_context():
        # Garantir que tabelas existem
        db.create_all()
        
        # Verificar se admin já existe
        admin = User.query.filter_by(username='thiagolobo').first()
        if admin:
            print("⚠️  Usuário admin já existe!")
            print(f"   Username: {admin.username}")
            print(f"   Email: {admin.email}")
            return
        
        # Criar admin
        admin = User(
            username='thiagolobo',
            email='thiago@taskflowai.com',
            full_name='Thiago Lobo',
            is_admin=True,
            is_active=True,
            subscription_plan='business'
        )
        admin.set_password('#Wolf@1902')
        
        db.session.add(admin)
        db.session.commit()
        
        print("✓ Usuário admin criado com sucesso!")
        print()
        print("📋 Credenciais:")
        print(f"   Username: thiagolobo")
        print(f"   Email: thiago@taskflowai.com")
        print(f"   Password: #Wolf@1902")
        print()
        
        # Criar workspace padrão
        print("📁 Criando workspace padrão...")
        workspace = Workspace(
            name='Workspace Principal',
            slug='workspace-principal',
            owner_id=admin.id,
            description='Workspace principal do administrador'
        )
        db.session.add(workspace)
        workspace.members.append(admin)
        db.session.commit()
        
        print("✓ Workspace criado com sucesso!")
        print()


def show_status():
    """Mostra status do sistema"""
    print("📊 Status do TaskFlowAI")
    print("=" * 50)
    
    # Configurar ambiente
    os.environ['FLASK_ENV'] = 'production'
    
    try:
        from app import app, db
        from models import User, Workspace, Project, Task
        
        with app.app_context():
            # Estatísticas
            total_users = User.query.count()
            total_workspaces = Workspace.query.count()
            total_projects = Project.query.count()
            total_tasks = Task.query.count()
            admin_users = User.query.filter_by(is_admin=True).count()
            
            print(f"👥 Usuários: {total_users} (Admin: {admin_users})")
            print(f"📁 Workspaces: {total_workspaces}")
            print(f"📊 Projetos: {total_projects}")
            print(f"✅ Tarefas: {total_tasks}")
            print()
            
            # Verificar arquivo de banco de dados
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                size = os.path.getsize(db_path) / 1024  # KB
                print(f"💾 Banco de dados: {db_path}")
                print(f"   Tamanho: {size:.2f} KB")
            else:
                print("⚠️  Banco de dados não encontrado!")
            
            print()
            
    except Exception as e:
        print(f"❌ Erro ao verificar status: {str(e)}")
        print()


def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("TaskFlowAI - Sistema de Gerenciamento de Tarefas")
        print("=" * 50)
        print()
        print("Uso: python init_taskflowai.py [comando]")
        print()
        print("Comandos disponíveis:")
        print("  init         - Inicializar banco de dados")
        print("  admin        - Criar usuário administrador")
        print("  full         - Inicializar tudo (init + admin)")
        print("  status       - Mostrar status do sistema")
        print()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'init':
        init_database()
    
    elif command == 'admin':
        create_admin()
    
    elif command == 'full':
        init_database()
        create_admin()
        show_status()
    
    elif command == 'status':
        show_status()
    
    else:
        print(f"❌ Comando desconhecido: {command}")
        print()
        print("Comandos disponíveis: init, admin, full, status")
        sys.exit(1)


if __name__ == '__main__':
    main()
