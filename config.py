import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-taskflowai-2025'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-taskflowai-2025'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///taskflowai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'}
    
    # Stripe
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # SocketIO
    SOCKETIO_MESSAGE_QUEUE = None
    
    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Planos de assinatura
    PLANS = {
        'free': {
            'name': 'Free',
            'price': 0,
            'features': {
                'workspaces': 1,
                'projects': 3,
                'tasks': 100,
                'storage_mb': 100,
                'team_members': 3,
                'ai_requests': 10
            }
        },
        'pro': {
            'name': 'Pro',
            'price': 29.90,
            'stripe_price_id': 'price_pro_monthly',
            'features': {
                'workspaces': 5,
                'projects': 'unlimited',
                'tasks': 'unlimited',
                'storage_mb': 10000,
                'team_members': 20,
                'ai_requests': 500
            }
        },
        'business': {
            'name': 'Business',
            'price': 79.90,
            'stripe_price_id': 'price_business_monthly',
            'features': {
                'workspaces': 'unlimited',
                'projects': 'unlimited',
                'tasks': 'unlimited',
                'storage_mb': 100000,
                'team_members': 'unlimited',
                'ai_requests': 'unlimited'
            }
        }
    }

class DevelopmentConfig(Config):
    """Configuração de desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuração de produção"""
    DEBUG = False
    TESTING = False
    
    # Forçar HTTPS
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Configuração de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
