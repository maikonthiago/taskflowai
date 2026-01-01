import sys
import os
import importlib.util
from flask import Flask, Response, request

# ==========================================
# CONFIGURAÇÃO DE MANUTENÇÃO
# ==========================================
MAINTENANCE_CONFIG = {
    'PORTFOLIO': False,
    'OTICA': False,
    'CASADOCOCO': True,     # Deixei Casa do Coco True conforme seu último request
    'TASKFLOWAI': False
}
ADMIN_CONTACT = "Thiago Lobo"

# ==========================================
# CAMINHOS ABSOLUTOS (HARDCODED PARA SEGURANÇA)
# ==========================================
# Ajuste aqui se seu usuário não for 'lobtechsolutions'
USERNAME = 'lobtechsolutions'
HOME = f'/home/{USERNAME}'

# Path do Virtualenv do TaskFlowAI (Onde instalamos o Flask 2.2.5)
TASKFLOW_VENV = f'{HOME}/.virtualenvs/taskflowai/lib/python3.10/site-packages'

# ==========================================
# PREPARAÇÃO DO AMBIENTE
# ==========================================
# Força o Python a olhar para o Virtualenv do TaskFlowAI PRIMEIRO
if TASKFLOW_VENV not in sys.path:
    sys.path.insert(0, TASKFLOW_VENV)

# ==========================================
# APP GLOBAL
# ==========================================
application = Flask(__name__)

# ==========================================
# PÁGINA DE MANUTENÇÃO
# ==========================================
def get_maintenance_page():
    return f"""
    <!DOCTYPE html>
    <html><head><title>Manutenção</title>
    <style>body{{font-family:sans-serif;text-align:center;padding:50px;}}h1{{color:#d9534f;}}</style>
    </head><body>
    <h1>⚠️ Sistema em Manutenção</h1>
    <p>Voltaremos em breve.</p>
    <p>Contato: {ADMIN_CONTACT}</p>
    </body></html>
    """

@application.before_request
def check_maintenance():
    path = request.path
    is_otica = path.startswith('/oticalojaodooculos')
    is_casadococo = path.startswith('/casadococo')
    is_taskflow = path.startswith('/taskflowai')
    is_portfolio = not (is_otica or is_casadococo or is_taskflow)

    in_maintenance = False
    if is_portfolio and MAINTENANCE_CONFIG['PORTFOLIO']: in_maintenance = True
    elif is_otica and MAINTENANCE_CONFIG['OTICA']: in_maintenance = True
    elif is_casadococo and MAINTENANCE_CONFIG['CASADOCOCO']: in_maintenance = True
    elif is_taskflow and MAINTENANCE_CONFIG['TASKFLOWAI']: in_maintenance = True
        
    if in_maintenance:
        return Response(get_maintenance_page(), status=503, mimetype='text/html')

# ==========================================
# 1. PORTFÓLIO (RAIZ)
# ==========================================
try:
    pf_path = f'{HOME}/lobtech-briefing-system'
    if pf_path not in sys.path: sys.path.append(pf_path)
    from app import app as portfolio_app
    # Gambiarra segura: Se não achou, a rota '/' do Application (Flask vazio) assume
    # Mas se achou, precisamos conectar. 
    # Como já definimos 'application' globalmente, vamos importar as VIEWS do portfolio para ele.
    # (Simplificação: apenas rotas que não colidam funcionam)
except:
    pass

@application.route('/')
def index_root():
    # Tenta servir o portfolio se carregou, senão msg simples
    if 'portfolio_app' in locals():
        with portfolio_app.test_request_context('/'):
            return portfolio_app.full_dispatch_request()
    return "Portfolio System Active"

# ==========================================
# 2. TASKFLOW AI (CRÍTICO)
# ==========================================
@application.route('/taskflowai', defaults={'path': ''})
@application.route('/taskflowai/', defaults={'path': ''})
@application.route('/taskflowai/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def taskflowai_proxy(path):
    # Setup Paths
    tf_path = f'{HOME}/TaskFlowAI'
    
    # Backup sys.path
    old_path = sys.path.copy()
    
    try:
        # 1. Inserir paths do TaskFlow
        if tf_path not in sys.path: sys.path.insert(0, tf_path)
        if TASKFLOW_VENV not in sys.path: sys.path.insert(0, TASKFLOW_VENV)
        
        # 2. Carregar App
        # Remove cache antigo para garantir reload
        if 'app' in sys.modules: del sys.modules['app']
        if 'config' in sys.modules: del sys.modules['config']
        
        from app import app as tf_app
        
        # 3. Configurar prefixo para garantir links certos
        tf_app.config['APPLICATION_ROOT'] = '/taskflowai'
        
        # 4. Processar request
        # script_root é o segredo para url_for funcionar no subpath
        path_info = f"/{path}" if path else "/"
        if request.query_string: path_info += f"?{request.query_string.decode()}"
        
        with tf_app.test_request_context(path_info, method=request.method, 
                                       headers=dict(request.headers), data=request.get_data(),
                                       script_root='/taskflowai'):
            return tf_app.full_dispatch_request()
            
    except Exception as e:
        import traceback
        return f"Erro no TaskFlowAI: {str(e)} <br><pre>{traceback.format_exc()}</pre>", 500
    finally:
        # Restaura paths para não quebrar outros apps
        sys.path = old_path

# ==========================================
# 3. OUTROS SISTEMAS (Simplificados para focar no TaskFlow)
# ==========================================
# ... (Mantenha o código anterior para Ótica e Casa do Coco se precisar, 
# mas o foco agora é fazer o TaskFlow funcionar)
