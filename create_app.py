"""
TaskFlowAI - Application Factory
Função factory para criar instância da aplicação Flask
"""
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
from functools import wraps
from sqlalchemy import or_, func

from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from models import db


def create_app(config_name='development'):
    """
    Função factory para criar a aplicação Flask
    
    Args:
        config_name: Nome da configuração a usar (development, production, testing)
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Carregar configuração
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(config_name, DevelopmentConfig)
    app.config.from_object(config_class)
    
    # Configurar para funcionar em subpath /taskflowai (para PythonAnywhere)
    app.config['APPLICATION_ROOT'] = '/taskflowai'
    
    # Criar diretórios necessários
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static/avatars', exist_ok=True)
    
    # Inicializar extensões
    db.init_app(app)
    
    # Registrar blueprints e rotas
    with app.app_context():
        # Importar aqui para evitar import circular
        from app import (
            login_manager, jwt, socketio, ai_service,
            ensure_default_data
        )
        
        login_manager.init_app(app)
        jwt.init_app(app)
        
        # Inicializar banco de dados e dados padrão
        db.create_all()
        ensure_default_data()
    
    return app


def init_database(app):
    """
    Inicializa o banco de dados com dados padrão
    
    Args:
        app: Flask app instance
    """
    with app.app_context():
        db.create_all()
        
        # Importar funções de seed
        from app import ensure_default_data
        ensure_default_data()
        
        print("✓ Banco de dados inicializado com sucesso!")


def create_admin_user(app):
    """
    Cria usuário administrador padrão
    
    Args:
        app: Flask app instance
    """
    with app.app_context():
        from models import User, Workspace
        
        db.create_all()
        
        # Verificar se admin já existe
        admin = User.query.filter_by(username='thiagolobo').first()
        if admin:
            print("⚠ Usuário admin já existe!")
            return
        
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
        
        # Criar workspace padrão
        workspace = Workspace(
            name='Workspace Admin',
            slug='admin-workspace',
            owner_id=admin.id
        )
        db.session.add(workspace)
        workspace.members.append(admin)
        db.session.commit()
        
        print("✓ Usuário admin criado com sucesso!")
        print("  Username: thiagolobo")
        print("  Email: thiago@taskflowai.com")
        print("  Password: #Wolf@1902")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'init':
            # Inicializar banco de dados
            app = create_app('production')
            init_database(app)
            
        elif command == 'create-admin':
            # Criar usuário admin
            app = create_app('production')
            create_admin_user(app)
            
        elif command == 'run':
            # Rodar aplicação
            env = sys.argv[2] if len(sys.argv) > 2 else 'development'
            app = create_app(env)
            
            from app import socketio
            socketio.run(app, debug=(env == 'development'), host='0.0.0.0', port=5000)
        else:
            print("Comandos disponíveis:")
            print("  python create_app.py init              - Inicializar banco de dados")
            print("  python create_app.py create-admin      - Criar usuário administrador")
            print("  python create_app.py run [env]         - Rodar aplicação (development/production)")
    else:
        print("Uso: python create_app.py [comando]")
        print("\nComandos disponíveis:")
        print("  init              - Inicializar banco de dados")
        print("  create-admin      - Criar usuário administrador")
        print("  run [env]         - Rodar aplicação (development/production)")
