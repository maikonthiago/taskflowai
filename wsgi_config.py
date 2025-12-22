#!/usr/bin/env python3
"""
WSGI Configuration for PythonAnywhere - TaskFlowAI
Deploy em: https://www.lobtechsolutions.com.br/taskflowai/
"""

import sys
import os

# Adicionar paths do projeto
project_home = '/home/lobtechsolutions/taskflowai'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Ativar virtualenv
activate_this = '/home/lobtechsolutions/taskflowai/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as file_:
        exec(file_.read(), dict(__file__=activate_this))

# Importar aplicação
from backend.app import app as application

# Configurar para subpath
application.config['APPLICATION_ROOT'] = '/taskflowai'

# Middleware para subpath
class PrefixMiddleware:
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return [b"Not Found"]

application.wsgi_app = PrefixMiddleware(application.wsgi_app, prefix='/taskflowai')
