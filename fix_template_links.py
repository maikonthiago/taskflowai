#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir todos os links dos templates adicionando o prefixo /taskflowai
"""

import os
import re

# Diretório dos templates
TEMPLATES_DIR = '/home/thiagolobopersonaltrainer/TaskFlowAI/templates'

# Padrão para encontrar hrefs que começam com /
PATTERN = r'href="(/[^"]*)"'

# Rotas que devem ter o prefixo /taskflowai
def should_add_prefix(path):
    """Verifica se o caminho precisa do prefixo"""
    # Não adicionar para âncoras (#), externos (http), ou já tem taskflowai
    if path.startswith('#') or path.startswith('http') or '/taskflowai' in path:
        return False
    # Não adicionar para static files
    if path.startswith('/static'):
        return False
    return True

def fix_template(file_path):
    """Corrige os links em um template"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    def replace_href(match):
        original_path = match.group(1)
        if should_add_prefix(original_path):
            return f'href="/taskflowai{original_path}"'
        return match.group(0)
    
    content = re.sub(PATTERN, replace_href, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("🔧 Corrigindo links nos templates...")
    print("")
    
    fixed_count = 0
    
    # Percorrer todos os arquivos .html no diretório templates
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, TEMPLATES_DIR)
                
                if fix_template(file_path):
                    print(f"✅ {relative_path}")
                    fixed_count += 1
                else:
                    print(f"⏭️  {relative_path} (sem alterações)")
    
    print("")
    print(f"✅ Total de arquivos corrigidos: {fixed_count}")
    print("")
    print("📝 Próximos passos:")
    print("   1. Teste os links no navegador")
    print("   2. Verifique se todas as páginas estão acessíveis")
    print("   3. Faça commit das alterações: git add templates/ && git commit -m 'Fix: Add /taskflowai prefix to all template links'")

if __name__ == '__main__':
    main()
