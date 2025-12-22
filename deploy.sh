#!/bin/bash

# Script de deploy automatizado para PythonAnywhere
# Usage: bash deploy.sh

set -e

echo "🚀 Iniciando deploy do TaskFlowAI..."

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar se está no diretório correto
if [ ! -f "app.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    exit 1
fi

# 1. Git - Commit e Push
echo -e "${YELLOW}📦 Fazendo commit das alterações...${NC}"
git add .
read -p "Mensagem do commit: " commit_msg
git commit -m "$commit_msg" || echo "Nada para commitar"

echo -e "${YELLOW}⬆️  Fazendo push para o GitHub...${NC}"
git push origin main

# 2. Comandos para executar no PythonAnywhere
echo -e "${GREEN}✅ Push concluído!${NC}"
echo ""
echo "Agora execute os seguintes comandos no console do PythonAnywhere:"
echo "================================================================"
echo ""
echo "cd ~/TaskFlowAI"
echo "git pull origin main"
echo "workon taskflowai"
echo "pip install -r requirements.txt"
echo "python -c 'from app import app, db; app.app_context().push(); db.create_all()'"
echo "touch /var/www/lobtechsolutions_pythonanywhere_com_wsgi.py"
echo ""
echo "================================================================"
echo ""
echo "Ou use este comando único:"
echo "cd ~/TaskFlowAI && git pull && workon taskflowai && pip install -q -r requirements.txt && touch /var/www/lobtechsolutions_pythonanywhere_com_wsgi.py"
echo ""
echo -e "${GREEN}✅ Deploy preparado! Execute os comandos acima no PythonAnywhere.${NC}"
