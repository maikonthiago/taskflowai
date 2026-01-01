import sys
import os
import importlib.util
from flask import Flask, Response, request

# ==========================================
# 1. CONFIGURAÇÃO BASE
# ==========================================
USERNAME = 'lobtechsolutions'
HOME = f'/home/{USERNAME}'

# Virtualenvs
VENV_TASKFLOW = f'{HOME}/.virtualenvs/taskflowai/lib/python3.10/site-packages'
VENV_OTICA = f'{HOME}/.virtualenvs/oticalojaodooculos/lib/python3.10/site-packages'
VENV_COCO = f'{HOME}/casadococo/venv/lib/python3.10/site-packages'

# Manutenção
MAINTENANCE_CONFIG = {
    'PORTFOLIO': False,
    'OTICA': False,
    'CASADOCOCO': False,
    'TASKFLOWAI': False
}
ADMIN_CONTACT = "Thiago Lobo"

# ==========================================
# 2. CARREGAMENTO DO SISTEMA PRINCIPAL (PORTFÓLIO)
# ==========================================
# O Portfólio é o "dono" do objeto application.
project_home = f'{HOME}/lobtech-briefing-system'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

try:
    # Tenta carregar o app nativo
    from app import app as application
    # Garante produção
    if hasattr(application, 'config'):
        application.config['DEBUG'] = False
except ImportError:
    # Fallback apenas se falhar catastroficamente
    application = Flask(__name__)
    @application.route('/')
    def fallback(): return "Erro ao carregar Portfólio (Main System)"

# ==========================================
# 3. MIDDLEWARE DE MANUTENÇÃO
# ==========================================
@application.before_request
def check_maintenance():
    path = request.path
    is_otica = path.startswith('/oticalojaodooculos')
    is_casadococo = path.startswith('/casadococo')
    is_taskflow = path.startswith('/taskflowai')
    is_portfolio = not (is_otica or is_casadococo or is_taskflow)

    allowed = True
    if is_portfolio and MAINTENANCE_CONFIG['PORTFOLIO']: allowed = False
    elif is_otica and MAINTENANCE_CONFIG['OTICA']: allowed = False
    elif is_casadococo and MAINTENANCE_CONFIG['CASADOCOCO']: allowed = False
    elif is_taskflow and MAINTENANCE_CONFIG['TASKFLOWAI']: allowed = False
        
    if not allowed:
        return f"""
        <html><body style='text-align:center;padding:50px;font-family:sans-serif;'>
        <h1 style='color:#e74c3c'>⚠️ Em Manutenção</h1>
        <p>Voltaremos em breve.</p>
        <p>Contato: {ADMIN_CONTACT}</p>
        </body></html>
        """, 503

# ==========================================
# 4. TASKFLOW AI (SISTEMA SECUNDÁRIO)
# ==========================================
@application.route('/taskflowai', defaults={'path': ''})
@application.route('/taskflowai/', defaults={'path': ''})
@application.route('/taskflowai/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'])
def taskflowai_proxy(path):
    tf_path = f'{HOME}/TaskFlowAI'
    old_sys_path = sys.path.copy()
    
    try:
        # Isolamento Completo
        if VENV_TASKFLOW not in sys.path: sys.path.insert(0, VENV_TASKFLOW)
        if tf_path not in sys.path: sys.path.insert(0, tf_path)
        
        # Limpa cache do Portfólio para carregar TaskFlow
        for mod in ['app', 'config', 'models', 'ai_service']:
            if mod in sys.modules: del sys.modules[mod]
        
        from app import app as tf_app
        
        tf_app.config['APPLICATION_ROOT'] = '/taskflowai'
        
        path_info = f"/{path}" if path else "/"
        if request.query_string: path_info += f"?{request.query_string.decode()}"
        
        # Environ base para corrigir links
        with tf_app.test_request_context(path_info, method=request.method,
                                       headers=dict(request.headers), data=request.get_data(),
                                       environ_base={'SCRIPT_NAME': '/taskflowai'}):
            return tf_app.full_dispatch_request()
    except Exception as e:
        import traceback
        return f"Erro TaskFlow: {str(e)}", 500
    finally:
        sys.path = old_sys_path
        # Limpa o TaskFlow da memória para o próximo request do Portfólio não quebrar
        # IMPORTANTE: Em WSGI isso é arriscado mas necessário nessa arquitetura mista
        for mod in ['app', 'config', 'models']:
            if mod in sys.modules: del sys.modules[mod]

# ==========================================
# 5. OTICA (SISTEMA SECUNDÁRIO)
# ==========================================
@application.route('/oticalojaodooculos/api/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def otica_proxy(path):
    p_path = f'{HOME}/oticalojaodooculos/backend'
    old_sys_path = sys.path.copy()
    try:
        if VENV_OTICA not in sys.path: sys.path.insert(0, VENV_OTICA)
        if p_path not in sys.path: sys.path.insert(0, p_path)
        for mod in ['app', 'config', 'models']: 
            if mod in sys.modules: del sys.modules[mod]
            
        spec = importlib.util.spec_from_file_location("otica_app", f"{p_path}/app.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["otica_app"] = mod
        spec.loader.exec_module(mod)
        app_runs = mod.create_app('production')
        
        full_path = f"/api/v1/{path}"
        if request.query_string: full_path += f"?{request.query_string.decode()}"
        
        with app_runs.test_request_context(full_path, method=request.method,
                                           headers=dict(request.headers), data=request.get_data()):
            return app_runs.full_dispatch_request()
    finally:
        sys.path = old_sys_path

@application.route('/oticalojaodooculos/')
@application.route('/oticalojaodooculos')
def otica_index():
    from flask import send_from_directory
    return send_from_directory(f'{HOME}/oticalojaodooculos/frontend', 'login.html')

@application.route('/oticalojaodooculos/<path:path>')
def otica_static(path):
    from flask import send_from_directory, jsonify
    base = f'{HOME}/oticalojaodooculos/frontend'
    f = os.path.join(base, path)
    if os.path.exists(f) and os.path.isfile(f):
        return send_from_directory(os.path.dirname(f), os.path.basename(f))
    if not path.startswith('api/'): return send_from_directory(base, 'login.html')
    return jsonify({'error': '404'}), 404

# ==========================================
# 6. CASA DO COCO (SISTEMA SECUNDÁRIO)
# ==========================================
@application.route('/casadococo', defaults={'path': ''})
@application.route('/casadococo/', defaults={'path': ''})
@application.route('/casadococo/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def coco_proxy(path):
    p_path = f'{HOME}/casadococo'
    old_sys_path = sys.path.copy()
    try:
        if VENV_COCO not in sys.path: sys.path.insert(0, VENV_COCO)
        if p_path not in sys.path: sys.path.insert(0, p_path)
        for mod in ['app', 'config', 'models']: 
            if mod in sys.modules: del sys.modules[mod]

        spec = importlib.util.spec_from_file_location("coco_app", f"{p_path}/app.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["coco_app"] = mod
        spec.loader.exec_module(mod)
        
        path_info = f"/{path}" if path else "/"
        if request.query_string: path_info += f"?{request.query_string.decode()}"
        
        with mod.app.test_request_context(path_info, method=request.method,
                                          headers=dict(request.headers), data=request.get_data()):
            return mod.app.full_dispatch_request()
    finally:
        sys.path = old_sys_path
