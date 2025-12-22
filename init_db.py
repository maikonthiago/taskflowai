#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para inicializar o banco de dados do TaskFlowAI
Este script evita problemas com caracteres especiais no bash
"""

import sys
import os

# Adicionar o diretório do projeto ao path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv(os.path.join(project_dir, '.env'))

print("🔄 Inicializando banco de dados...")

try:
    from app import app, db
    
    with app.app_context():
        # Criar todas as tabelas
        db.create_all()
        print("✅ Banco de dados inicializado com sucesso!")
        print("")
        print("📊 Tabelas criadas:")
        
        # Listar todas as tabelas criadas
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        for i, table in enumerate(tables, 1):
            print(f"   {i}. {table}")
        
        print("")
        print(f"✅ Total: {len(tables)} tabelas criadas")
        
except Exception as e:
    print(f"❌ Erro ao inicializar banco de dados: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
