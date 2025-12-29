import sys
import os

# ==========================================
# PORTFÓLIO - Raiz do domínio
# ==========================================
project_home = '/home/lobtechsolutions/lobtech-briefing-system'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application
application.config['DEBUG'] = False


# ==========================================
# SISTEMA ÓTICA - /oticalojaodooculos
# ==========================================

# Cache global para o app da ótica (será criado na primeira requisição)
_otica_app_cache = None

def get_otica_app():
    """
    Função para criar app da ótica com ambiente isolado
    Usa cache para evitar recriar o app a cada requisição
    """
    global _otica_app_cache

    # Se já existe no cache, retornar
    if _otica_app_cache is not None:
        return _otica_app_cache

    import sys
    import os
    import importlib.util

    # Definir paths da ótica
    otica_backend_path = '/home/lobtechsolutions/oticalojaodooculos/backend'
    otica_venv_path = '/home/lobtechsolutions/.virtualenvs/oticalojaodooculos/lib/python3.10/site-packages'

    # Salvar sys.path e sys.modules originais
    original_sys_path = sys.path.copy()
    modules_to_restore = {}

    # Módulos que podem causar conflito
    conflicting_modules = ['models', 'app', 'config']

    # Salvar e remover módulos conflitantes
    for mod_name in conflicting_modules:
        if mod_name in sys.modules:
            modules_to_restore[mod_name] = sys.modules[mod_name]
            del sys.modules[mod_name]

    try:
        # Substituir sys.path completamente
        sys.path = [
            otica_backend_path,
            otica_venv_path,
            '/usr/lib/python3.10',
            '/usr/lib/python3.10/lib-dynload',
        ]

        # Configurar variáveis de ambiente da ótica
        os.environ['FLASK_ENV'] = 'production'
        os.environ['DATABASE_URL'] = 'sqlite:////home/lobtechsolutions/oticalojaodooculos/backend/instance/suaotica.db'

        # Carregar o módulo app.py da ótica usando nome único
        spec = importlib.util.spec_from_file_location(
            "otica_app_module_isolated",
            os.path.join(otica_backend_path, "app.py")
        )
        otica_app_module = importlib.util.module_from_spec(spec)

        # Adicionar ao sys.modules com nome único
        sys.modules["otica_app_module_isolated"] = otica_app_module

        # Executar o módulo
        spec.loader.exec_module(otica_app_module)

        # Criar a aplicação da ótica
        otica_app = otica_app_module.create_app('production')

        # Guardar no cache
        _otica_app_cache = otica_app

        return otica_app

    finally:
        # Restaurar sys.path
        sys.path = original_sys_path

        # Restaurar módulos que foram removidos
        for mod_name, mod_obj in modules_to_restore.items():
            sys.modules[mod_name] = mod_obj


# Rotas API da ótica
@application.route('/oticalojaodooculos/api/v1/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'])
def otica_api(path):
    """
    Roteador para API da ótica em /oticalojaodooculos/api/v1/*
    """
    from flask import request
    from werkzeug.datastructures import Headers

    # Construir path completo da API
    full_path = f'/api/v1/{path}'

    # Adicionar query string ao path se existir
    if request.query_string:
        full_path = f'{full_path}?{request.query_string.decode("utf-8")}'

    # Copiar headers para estrutura mutável
    mutable_headers = Headers()
    for key, value in request.headers:
        # Pular headers problemáticos que o Flask recriará
        if key.lower() not in ('content-length', 'content-type', 'host'):
            mutable_headers[key] = value

    # Adicionar Content-Type se existir
    if request.content_type:
        mutable_headers['Content-Type'] = request.content_type

    # Obter app (do cache ou criar)
    otica_app = get_otica_app()

    # path como argumento posicional e headers como dict
    with otica_app.test_request_context(
        full_path,
        method=request.method,
        headers=dict(mutable_headers),
        data=request.get_data()
    ):
        try:
            # Processar requisição completa
            response = otica_app.full_dispatch_request()
            return response
        except Exception as e:
            # Log do erro
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro na API da ótica: {error_details}")

            # Retornar erro formatado
            from flask import jsonify
            return jsonify({
                'error': 'Erro interno no servidor',
                'message': str(e),
                'type': type(e).__name__
            }), 500


@application.route('/oticalojaodooculos/health')
def otica_health():
    """
    Health check específico da ótica
    """
    try:
        otica_app = get_otica_app()
        with otica_app.test_request_context('/health', method='GET'):
            response = otica_app.full_dispatch_request()
            return response
    except Exception as e:
        from flask import jsonify
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==========================================
# SERVIR ARQUIVOS ESTÁTICOS DA ÓTICA
# ==========================================

@application.route('/oticalojaodooculos/')
@application.route('/oticalojaodooculos')
def otica_index():
    """
    Serve o index.html da ótica
    """
    from flask import send_from_directory
    static_path = '/home/lobtechsolutions/lobtech-briefing-system/static/oticalojaodooculos'
    return send_from_directory(static_path, 'index.html')


@application.route('/oticalojaodooculos/<path:path>')
def otica_static(path):
    """
    Serve arquivos estáticos da ótica (JS, CSS, imagens)
    """
    from flask import send_from_directory
    import os

    static_path = '/home/lobtechsolutions/lobtech-briefing-system/static/oticalojaodooculos'
    file_path = os.path.join(static_path, path)

    # Se o arquivo existir, servir
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(static_path, path)

    # Se não encontrar e NÃO for rota da API, retorna index.html (SPA routing)
    if not path.startswith('api/'):
        return send_from_directory(static_path, 'index.html')

    # Se for rota da API que não existe, retornar 404
    from flask import jsonify
    return jsonify({'error': 'Recurso não encontrado'}), 404


# ==========================================
# SISTEMA CASA DO COCO - /casadococo
# ==========================================

# Cache global para o app (será criado na primeira requisição)
_casadococo_app_cache = None

def get_casadococo_app():
    """
    Função para criar app da Casa do Coco com ambiente isolado
    Usa cache para evitar recriar o app a cada requisição
    """
    global _casadococo_app_cache

    # Se já existe no cache, retornar
    if _casadococo_app_cache is not None:
        return _casadococo_app_cache

    import sys
    import os
    import importlib.util

    # Definir paths da Casa do Coco
    casadococo_path = '/home/lobtechsolutions/casadococo'
    casadococo_venv_path = '/home/lobtechsolutions/casadococo/venv/lib/python3.10/site-packages'

    # Salvar sys.path e sys.modules originais
    original_sys_path = sys.path.copy()
    modules_to_restore = {}

    # Módulos que podem causar conflito
    conflicting_modules = ['models', 'app', 'config']

    # Salvar e remover módulos conflitantes
    for mod_name in conflicting_modules:
        if mod_name in sys.modules:
            modules_to_restore[mod_name] = sys.modules[mod_name]
            del sys.modules[mod_name]

    try:
        # Substituir sys.path completamente (sem os paths da ótica)
        sys.path = [
            casadococo_path,
            casadococo_venv_path,
            '/usr/lib/python3.10',
            '/usr/lib/python3.10/lib-dynload',
        ]

        # Configurar variáveis de ambiente
        os.environ['FLASK_ENV'] = 'production'

        # Carregar app.py da Casa do Coco usando nome único
        spec = importlib.util.spec_from_file_location(
            "casadococo_app_module_isolated",
            os.path.join(casadococo_path, "app.py")
        )
        casadococo_module = importlib.util.module_from_spec(spec)

        # Adicionar ao sys.modules com nome único para evitar conflito
        sys.modules["casadococo_app_module_isolated"] = casadococo_module

        # Executar o módulo
        spec.loader.exec_module(casadococo_module)

        # Obter a aplicação
        casadococo_app = casadococo_module.app

        # Configurar para subpath
        casadococo_app.config['APPLICATION_ROOT'] = '/casadococo'
        casadococo_app.config['DEBUG'] = False
        casadococo_app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{casadococo_path}/casadococo.db'

        # Guardar no cache
        _casadococo_app_cache = casadococo_app

        return casadococo_app

    finally:
        # Restaurar sys.path
        sys.path = original_sys_path

        # Restaurar módulos que foram removidos
        for mod_name, mod_obj in modules_to_restore.items():
            sys.modules[mod_name] = mod_obj


@application.route('/casadococo')
@application.route('/casadococo/')
@application.route('/casadococo/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'])
def casadococo_route(path=''):
    """
    Roteador principal para Casa do Coco em /casadococo/*
    """
    from flask import request
    from werkzeug.datastructures import Headers

    # Obter app (do cache ou criar)
    casadococo_app = get_casadococo_app()

    # Construir path correto
    if path:
        full_path = f'/{path}'
    else:
        full_path = '/'

    # Adicionar query string ao path se existir
    if request.query_string:
        full_path = f'{full_path}?{request.query_string.decode("utf-8")}'

    # Copiar headers para estrutura mutável
    mutable_headers = Headers()
    for key, value in request.headers:
        if key.lower() not in ('content-length', 'content-type', 'host'):
            mutable_headers[key] = value

    if request.content_type:
        mutable_headers['Content-Type'] = request.content_type

    # Processar requisição no contexto da Casa do Coco
    with casadococo_app.test_request_context(
        full_path,
        method=request.method,
        headers=dict(mutable_headers),
        data=request.get_data()
    ):
        try:
            # Processar requisição completa
            response = casadococo_app.full_dispatch_request()
            return response
        except Exception as e:
            # Log do erro
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro na Casa do Coco: {error_details}")

            # Retornar erro formatado
            from flask import jsonify
            return jsonify({
                'error': 'Erro interno no servidor',
                'message': str(e),
                'type': type(e).__name__
            }), 500


@application.route('/casadococo/health')
def casadococo_health():
    """
    Health check específico da Casa do Coco
    """
    try:
        casadococo_app = get_casadococo_app()
        with casadococo_app.test_request_context('/'):
            from flask import jsonify
            return jsonify({
                'status': 'ok',
                'app': 'Casa do Coco',
                'version': '1.0.0'
            })
    except Exception as e:
        from flask import jsonify
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ==========================================
# SISTEMA TASKFLOWAI - /taskflowai
# ==========================================

# Cache global para o app (será criado na primeira requisição)
_taskflowai_app_cache = None

def get_taskflowai_app():
    """
    Função para criar app do TaskFlowAI com ambiente isolado
    Usa cache para evitar recriar o app a cada requisição
    """
    global _taskflowai_app_cache

    # Se já existe no cache, retornar
    if _taskflowai_app_cache is not None:
        return _taskflowai_app_cache

    import sys
    import os
    import importlib.util

    # Definir paths do TaskFlowAI
    taskflowai_path = '/home/lobtechsolutions/TaskFlowAI/taskflowai'
    taskflowai_venv_path = '/home/lobtechsolutions/.virtualenvs/taskflowai/lib/python3.10/site-packages'

    # Salvar sys.path e sys.modules originais
    original_sys_path = sys.path.copy()
    modules_to_restore = {}

    # Módulos que podem causar conflito
    conflicting_modules = ['models', 'app', 'config', 'ai_service', 'stripe_payment']

    # Salvar e remover módulos conflitantes
    for mod_name in conflicting_modules:
        if mod_name in sys.modules:
            modules_to_restore[mod_name] = sys.modules[mod_name]
            del sys.modules[mod_name]

    try:
        # Substituir sys.path completamente
        sys.path = [
            taskflowai_path,
            taskflowai_venv_path,
            '/usr/lib/python3.10',
            '/usr/lib/python3.10/lib-dynload',
        ]

        # Configurar variáveis de ambiente
        os.environ['FLASK_ENV'] = 'production'

        # Carregar app.py do TaskFlowAI usando nome único
        spec = importlib.util.spec_from_file_location(
            "taskflowai_app_module_isolated",
            os.path.join(taskflowai_path, "app.py")
        )
        taskflowai_module = importlib.util.module_from_spec(spec)

        # Adicionar ao sys.modules com nome único para evitar conflito
        sys.modules["taskflowai_app_module_isolated"] = taskflowai_module

        # Executar o módulo
        spec.loader.exec_module(taskflowai_module)

        # Obter a aplicação
        taskflowai_app = taskflowai_module.app

        # Configurar para subpath
        taskflowai_app.config['APPLICATION_ROOT'] = '/taskflowai'
        taskflowai_app.config['DEBUG'] = False

        # Guardar no cache
        _taskflowai_app_cache = taskflowai_app

        return taskflowai_app

    finally:
        # Restaurar sys.path
        sys.path = original_sys_path

        # Restaurar módulos que foram removidos
        for mod_name, mod_obj in modules_to_restore.items():
            sys.modules[mod_name] = mod_obj


@application.route('/taskflowai')
@application.route('/taskflowai/')
@application.route('/taskflowai/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH', 'HEAD'])
def taskflowai_route(path=''):
    """
    Roteador principal para TaskFlowAI em /taskflowai/*
    """
    from flask import request
    from werkzeug.datastructures import Headers

    # Obter app (do cache ou criar)
    taskflowai_app = get_taskflowai_app()

    # Construir path correto
    if path:
        full_path = f'/{path}'
    else:
        full_path = '/'

    # Adicionar query string ao path se existir
    if request.query_string:
        full_path = f'{full_path}?{request.query_string.decode("utf-8")}'

    # Copiar headers para estrutura mutável
    mutable_headers = Headers()
    for key, value in request.headers:
        if key.lower() not in ('content-length', 'content-type', 'host'):
            mutable_headers[key] = value

    if request.content_type:
        mutable_headers['Content-Type'] = request.content_type

    # Processar requisição no contexto do TaskFlowAI
    with taskflowai_app.test_request_context(
        full_path,
        method=request.method,
        headers=dict(mutable_headers),
        data=request.get_data()
    ):
        try:
            # Processar requisição completa
            response = taskflowai_app.full_dispatch_request()
            return response
        except Exception as e:
            # Log do erro
            import traceback
            error_details = traceback.format_exc()
            print(f"Erro no TaskFlowAI: {error_details}")

            # Retornar erro formatado
            from flask import jsonify
            return jsonify({
                'error': 'Erro interno no servidor',
                'message': str(e),
                'type': type(e).__name__
            }), 500


@application.route('/taskflowai/health')
def taskflowai_health():
    """
    Health check específico do TaskFlowAI
    """
    try:
        taskflowai_app = get_taskflowai_app()
        with taskflowai_app.test_request_context('/'):
            from flask import jsonify
            return jsonify({
                'status': 'ok',
                'app': 'TaskFlowAI',
                'version': '1.0.0'
            })
    except Exception as e:
        from flask import jsonify
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
