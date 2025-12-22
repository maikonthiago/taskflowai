from flask import Flask, render_template, send_from_directory
from backend.database import db
from backend.routes import register_routes
from backend.routes_admin import admin_bp
from backend.routes_pricing import pricing_bp
from ai.ai_service import create_ai_routes
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__, 
            static_folder='../frontend/static', 
            template_folder='../frontend/templates')

# Configurações
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///taskflowai.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

CORS(app)
jwt = JWTManager(app)

# Inicializar database
db.init_app(app)

# Registrar rotas da API
register_routes(app)
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(pricing_bp, url_prefix='/api/pricing')
create_ai_routes(app)

# Rotas de páginas
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/tasks')
def tasks():
    return render_template('tasks.html')

@app.route('/project/<int:project_id>')
def project(project_id):
    return render_template('project.html', project_id=project_id)

@app.route('/kanban')
def kanban():
    return render_template('kanban.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/document')
def document():
    return render_template('document.html')

@app.route('/whiteboard')
def whiteboard():
    return render_template('whiteboard.html')

@app.route('/pricing')
def pricing_page():
    return render_template('pricing.html')

@app.route('/checkout/<plan_id>')
def checkout(plan_id):
    return render_template('checkout.html', plan_id=plan_id)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
