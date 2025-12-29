#!/usr/bin/env python3
"""
TaskFlowAI - Script de Correção de Templates
Ajusta todos os links e caminhos nos templates para funcionar com subpath /taskflowai
"""
import os
import re
from pathlib import Path


def fix_static_links(content):
    """
    Corrige links de arquivos estáticos
    """
    # /static/ -> /taskflowai/static/
    content = re.sub(
        r'(href|src)=["\']\/static\/',
        r'\1="/taskflowai/static/',
        content
    )
    
    # Garantir que já tem /taskflowai não duplica
    content = content.replace('/taskflowai/taskflowai/', '/taskflowai/')
    
    return content


def fix_route_links(content):
    """
    Corrige links de rotas (hrefs)
    """
    routes = [
        'login', 'register', 'logout', 'dashboard', 'pricing',
        'workspace', 'project', 'tasks', 'task', 'kanban',
        'calendar', 'chat', 'documents', 'settings', 'subscription',
        'admin'
    ]
    
    for route in routes:
        # Padrão: href="/{route}" -> href="/taskflowai/{route}"
        pattern = rf'href=["\']\/{route}'
        replacement = rf'href="/taskflowai/{route}'
        content = re.sub(pattern, replacement, content)
    
    # href="/" (root) -> href="/taskflowai/"
    content = re.sub(r'href=["\']\/["\']', 'href="/taskflowai/"', content)
    
    # Garantir que já tem /taskflowai não duplica
    content = content.replace('/taskflowai/taskflowai/', '/taskflowai/')
    
    return content


def fix_api_calls(content):
    """
    Corrige chamadas de API em JavaScript
    """
    # fetch('/api/...') -> fetch('/taskflowai/api/...')
    content = re.sub(
        r'(fetch\(["\'])(\/api\/)',
        r'\1/taskflowai/api/',
        content
    )
    
    # $.ajax({ url: '/api/...' }) -> url: '/taskflowai/api/...'
    content = re.sub(
        r'(url:\s*["\'])(\/api\/)',
        r'\1/taskflowai/api/',
        content
    )
    
    # axios.get('/api/...') -> axios.get('/taskflowai/api/...')
    content = re.sub(
        r'(axios\.(get|post|put|delete|patch)\(["\'])(\/api\/)',
        r'\1/taskflowai/api/',
        content
    )
    
    # Garantir que já tem /taskflowai não duplica
    content = content.replace('/taskflowai/taskflowai/', '/taskflowai/')
    
    return content


def fix_form_actions(content):
    """
    Corrige actions de formulários
    """
    # action="/login" -> action="/taskflowai/login"
    content = re.sub(
        r'action=["\']\/([a-zA-Z])',
        r'action="/taskflowai/\1',
        content
    )
    
    # Garantir que já tem /taskflowai não duplica
    content = content.replace('/taskflowai/taskflowai/', '/taskflowai/')
    
    return content


def process_file(file_path):
    """
    Processa um arquivo aplicando todas as correções
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar correções
        content = fix_static_links(content)
        content = fix_route_links(content)
        content = fix_api_calls(content)
        content = fix_form_actions(content)
        
        # Verificar se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"   ❌ Erro ao processar {file_path}: {str(e)}")
        return False


def process_directory(directory, pattern='*.html'):
    """
    Processa todos os arquivos em um diretório
    """
    path = Path(directory)
    files = list(path.glob(pattern))
    
    if not files:
        return 0
    
    print(f"\n📁 Processando {directory}...")
    print("=" * 60)
    
    modified = 0
    for file_path in files:
        if process_file(file_path):
            print(f"   ✓ Modificado: {file_path.name}")
            modified += 1
        else:
            print(f"   - Sem alterações: {file_path.name}")
    
    return modified


def main():
    """
    Função principal
    """
    print("🔧 TaskFlowAI - Correção de Templates")
    print("=" * 60)
    print("Este script irá ajustar todos os links nos templates")
    print("para funcionarem com o subpath /taskflowai")
    print()
    
    # Obter diretório do script
    script_dir = Path(__file__).parent
    
    # Diretórios a processar
    directories = [
        ('templates', '*.html'),
        ('static/js', '*.js'),
        ('static/css', '*.css'),
    ]
    
    total_modified = 0
    
    for directory, pattern in directories:
        dir_path = script_dir / directory
        if dir_path.exists():
            modified = process_directory(dir_path, pattern)
            total_modified += modified
        else:
            print(f"\n⚠️  Diretório não encontrado: {directory}")
    
    print()
    print("=" * 60)
    if total_modified > 0:
        print(f"✓ Concluído! {total_modified} arquivo(s) modificado(s)")
    else:
        print("✓ Nenhuma alteração necessária")
    print()
    
    # Verificações adicionais
    print("📋 Verificações Recomendadas:")
    print("1. Revisar os arquivos modificados")
    print("2. Testar o sistema localmente antes do deploy")
    print("3. Fazer backup antes de aplicar no servidor")
    print()


if __name__ == '__main__':
    main()
