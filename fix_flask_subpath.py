#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar APPLICATION_ROOT ao Flask para subpath /taskflowai
"""

import os
import re

APP_FILE = '/home/thiagolobopersonaltrainer/TaskFlowAI/app.py'

print("🔧 Configurando Flask para subpath /taskflowai...")

# Ler app.py
with open(APP_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Verificar se já tem APPLICATION_ROOT
if 'APPLICATION_ROOT' in content:
    print("⚠️  APPLICATION_ROOT já configurado")
else:
    # Adicionar após app.config.from_object
    old_section = "app.config.from_object(config[os.environ.get('FLASK_ENV', 'development')])"
    new_section = """app.config.from_object(config[os.environ.get('FLASK_ENV', 'development')])

# Configurar para funcionar em subpath /taskflowai
app.config['APPLICATION_ROOT'] = '/taskflowai'"""
    
    content = content.replace(old_section, new_section)
    
    # Salvar
    with open(APP_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ APPLICATION_ROOT configurado em app.py")

print("")
print("✅ Configuração completa!")
print("")
print("📝 Próximos passos no PythonAnywhere:")
print("   1. cd ~/TaskFlowAI")
print("   2. git pull origin main")
print("   3. Reload no Web tab")
