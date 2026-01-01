import sys
import os
import importlib.util
from flask import Flask, Response, request, redirect

# ==========================================
# CONFIGURAÇÃO DE MANUTENÇÃO POR SISTEMA
# ==========================================
MAINTENANCE_CONFIG = {
    'PORTFOLIO': False,      # Raiz (/)
    'OTICA': False,          # /oticalojaodooculos
    'CASADOCOCO': False,     # /casadococo
    'TASKFLOWAI': False      # /taskflowai
}

ADMIN_CONTACT = "Thiago Lobo"

# ==========================================
# CONFIGURAÇÃO GERAL
# ==========================================
HOME = os.path.expanduser('~')

def get_maintenance_page():
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Sistema em Manutenção</title>
        <style>
            body {{ font-family: sans-serif; background: #f8f9fa; display: flex; align-items: center; justify-content: center; height: 100vh; text-align: center; }}
            .container {{ background: white; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 500px; }}
            h1 {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>⚠️ Sistema em Manutenção</h1>
            <p>O serviço estará disponível em breve.</p>
            <p><strong>Contato: {ADMIN_CONTACT}</strong></p>
        </div>
    </body>
    </html>
    """

# ==========================================
# 1. PORTFÓLIO (SISTEMA PRINCIPAL)
# ==========================================
# Tenta carregar o sistema principal PRIMEIRO para ele ser o objeto 'application'
project_home = os.path.join(HOME, 'lobtech-briefing-system')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

try:
    # IMPORTANTE: Carrega o app original do portfólio
    from app import app as application
    # Garante que seja modo produção
    application.config['DEBUG'] = False
except ImportError:
    # Fallback se algo der muito errado
    application = Flask(__name__)
    @application.route('/')
    def index():
        return "Erro Crítico: Não foi possível carregar o sistema principal (Portfolio)."

# ==========================================
# MIDDLEWARE DE MANUTENÇÃO GLOBAL
# ==========================================
# Injetamos um handler antes de cada requisição para verificar manutenção
@application.before_request
def check_maintenance():
    path = request.path
    
    # Verifica qual sistema está sendo acessado
    is_otica = path.startswith('/oticalojaodooculos')
    is_casadococo = path.startswith('/casadococo')
    is_taskflow = path.startswith('/taskflowai')
    
    # Se não for nenhum dos sub-sistemas, é o Portfolio (Raiz)
    is_portfolio = not (is_otica or is_casadococo or is_taskflow)

    # Checa a configuração correta
    in_maintenance = False
    
    if is_portfolio and MAINTENANCE_CONFIG['PORTFOLIO']:
        in_maintenance = True
    elif is_otica and MAINTENANCE_CONFIG['OTICA']:
        in_maintenance = True
    elif is_casadococo and MAINTENANCE_CONFIG['CASADOCOCO']:
        in_maintenance = True
    elif is_taskflow and MAINTENANCE_CONFIG['TASKFLOWAI']:
        in_maintenance = True
        
    if in_maintenance:
        return Response(get_maintenance_page(), status=503, mimetype='text/html')

# ==========================================
# 2. SISTEMA ÓTICA
# ==========================================
_otica_app_cache = None
def get_otica_app():
    global _otica_app_cache
    if _otica_app_cache: return _otica_app_cache
    
    # Setup de paths
    base = os.path.join(HOME, 'oticalojaodooculos/backend')
    venv = os.path.join(HOME, '.virtualenvs/oticalojaodooculos/lib/python3.10/site-packages')
    
    # Isola imports
    old_path = sys.path.copy()
    to_restore = {k: sys.modules[k] for k in ['models', 'app', 'config'] if k in sys.modules}
    for k in to_restore: del sys.modules[k]
    
    try:
        sys.path = [base, venv] + [p for p in old_path if p not in [base, venv]]
        os.environ['FLASK_ENV'] = 'production'
        os.environ['DATABASE_URL'] = f'sqlite:///{base}/instance/suaotica.db'
        
        spec = importlib.util.spec_from_file_location("otica_mod", os.path.join(base, "app.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["otica_mod"] = mod
        spec.loader.exec_module(mod)
        _otica_app_cache = mod.create_app('production')
        return _otica_app_cache
    finally:
        sys.path = old_path
        sys.modules.update(to_restore)

@application.route('/oticalojaodooculos/api/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'])
def otica_api(path):
    # Manutenção checada no before_request
    from werkzeug.datastructures import Headers
    full_path = f'/api/v1/{path}'
    if request.query_string: full_path += f'?{request.query_string.decode("utf-8")}'
    
    hdrs = Headers()
    for k, v in request.headers:
        if k.lower() not in ('content-length', 'content-type', 'host'): hdrs[k] = v
    if request.content_type: hdrs['Content-Type'] = request.content_type
        
    app = get_otica_app()
    with app.test_request_context(full_path, method=request.method, headers=dict(hdrs), data=request.get_data()):
        return app.full_dispatch_request()

@application.route('/oticalojaodooculos/')
@application.route('/oticalojaodooculos')
def otica_index():
    from flask import send_from_directory
    return send_from_directory(os.path.join(HOME, 'oticalojaodooculos/frontend'), 'login.html')

@application.route('/oticalojaodooculos/<path:path>')
def otica_static(path):
    from flask import send_from_directory, jsonify
    base = os.path.join(HOME, 'oticalojaodooculos/frontend')
    f = os.path.join(base, path)
    if os.path.exists(f) and os.path.isfile(f):
        return send_from_directory(os.path.dirname(f), os.path.basename(f))
    if not path.startswith('api/'):
        return send_from_directory(base, 'login.html')
    return jsonify({'error': 'Not found'}), 404

# ==========================================
# 3. SISTEMA CASA DO COCO
# ==========================================
_casadococo_app_cache = None
def get_casadococo_app():
    global _casadococo_app_cache
    if _casadococo_app_cache: return _casadococo_app_cache
    
    base = os.path.join(HOME, 'casadococo')
    venv = os.path.join(HOME, 'casadococo/venv/lib/python3.10/site-packages')
    
    old_path = sys.path.copy()
    to_restore = {k: sys.modules[k] for k in ['models', 'app', 'config'] if k in sys.modules}
    for k in to_restore: del sys.modules[k]
    
    try:
        sys.path = [base, venv] + [p for p in old_path if p not in [base, venv]]
        os.environ['FLASK_ENV'] = 'production'
        
        spec = importlib.util.spec_from_file_location("coco_mod", os.path.join(base, "app.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["coco_mod"] = mod
        spec.loader.exec_module(mod)
        
        app = mod.app
        app.config.update({
            'APPLICATION_ROOT': '/casadococo',
            'DEBUG': False,
            'SQLALCHEMY_DATABASE_URI': f'sqlite:///{base}/casadococo.db'
        })
        _casadococo_app_cache = app
        return app
    finally:
        sys.path = old_path
        sys.modules.update(to_restore)

@application.route('/casadococo', defaults={'path': ''})
@application.route('/casadococo/', defaults={'path': ''})
@application.route('/casadococo/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'])
def casadococo_route(path):
    from werkzeug.datastructures import Headers
    full_path = f'/{path}' if path else '/'
    if request.query_string: full_path += f'?{request.query_string.decode("utf-8")}'
    
    hdrs = Headers()
    for k, v in request.headers:
        if k.lower() not in ('content-length', 'content-type', 'host'): hdrs[k] = v
    if request.content_type: hdrs['Content-Type'] = request.content_type
        
    app = get_casadococo_app()
    with app.test_request_context(full_path, method=request.method, headers=dict(hdrs), data=request.get_data()):
        return app.full_dispatch_request()

@application.route('/casadococo/health')
def casadococo_health():
    from flask import jsonify
    try:
        get_casadococo_app()
        return jsonify({'status': 'ok'})
    except:
        return jsonify({'status': 'error'}), 500

# ==========================================
# 4. SISTEMA TASKFLOWAI
# ==========================================
_taskflowai_app_cache = None
def get_taskflowai_app():
    global _taskflowai_app_cache
    if _taskflowai_app_cache: return _taskflowai_app_cache
    
    base = os.path.join(HOME, 'TaskFlowAI')
    venv = os.path.join(HOME, '.virtualenvs/taskflowai/lib/python3.10/site-packages')
    
    old_path = sys.path.copy()
    to_restore = {k: sys.modules[k] for k in ['models', 'app', 'config', 'ai_service', 'stripe_payment'] if k in sys.modules}
    for k in to_restore: del sys.modules[k]
    
    try:
        sys.path = [base, venv] + [p for p in old_path if p not in [base, venv]]
        os.environ['FLASK_ENV'] = 'production'
        
        if os.path.exists(os.path.join(base, '.env')):
            from dotenv import load_dotenv
            load_dotenv(os.path.join(base, '.env'))
            
        spec = importlib.util.spec_from_file_location("taskflow_mod", os.path.join(base, "app.py"))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["taskflow_mod"] = mod
        spec.loader.exec_module(mod)
        
        app = mod.app
        app.config.update({
            'APPLICATION_ROOT': '/taskflowai',
            'DEBUG': False
        })
        _taskflowai_app_cache = app
        return app
    finally:
        sys.path = old_path
        sys.modules.update(to_restore)

@application.route('/taskflowai', defaults={'path': ''})
@application.route('/taskflowai/', defaults={'path': ''})
@application.route('/taskflowai/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'])
def taskflowai_route(path):
    from werkzeug.datastructures import Headers, ImmutableMultiDict
    path_info = f"/{path}" if path else "/"
    if request.query_string: path_info += f'?{request.query_string.decode("utf-8")}'
    
    hdrs = Headers()
    for k, v in request.headers:
        if k.lower() not in ('content-length', 'content-type', 'host'): hdrs[k] = v
    if request.content_type: hdrs['Content-Type'] = request.content_type
        
    try:
        app = get_taskflowai_app()
        # [FIX] script_root garante URLs corretas
        with app.test_request_context(path_info, method=request.method, headers=dict(hdrs), data=request.get_data(), script_root='/taskflowai'):
            return app.full_dispatch_request()
    except Exception as e:
        from flask import jsonify
        return jsonify({'error': 'Erro interno', 'details': str(e)}), 500

@application.route('/taskflowai/health')
def taskflowai_health():
    from flask import jsonify
    try:
        get_taskflowai_app()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'status': 'error', 'details': str(e)}), 500
