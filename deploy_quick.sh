#!/bin/bash
# =============================================================================
# TaskFlowAI - Script Rápido de Deploy no PythonAnywhere
# =============================================================================
# Este script automatiza os principais passos do deploy
# Execute linha por linha ou seções conforme necessário
# =============================================================================

echo "🚀 TaskFlowAI - Deploy no PythonAnywhere"
echo "=========================================="
echo ""

# =============================================================================
# PASSO 1: CRIAR VIRTUAL ENVIRONMENT
# =============================================================================
echo "📦 Passo 1: Criando Virtual Environment..."
echo ""
echo "Execute os comandos abaixo no console Bash do PythonAnywhere:"
echo ""
echo "cd /home/lobtechsolutions"
echo "mkvirtualenv taskflowai --python=python3.10"
echo "workon taskflowai"
echo ""
read -p "Pressione ENTER quando o virtualenv estiver criado e ativo..."

# =============================================================================
# PASSO 2: INSTALAR DEPENDÊNCIAS
# =============================================================================
echo ""
echo "📚 Passo 2: Instalando Dependências..."
echo ""
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso!"
else
    echo "❌ Erro ao instalar dependências. Verifique o requirements.txt"
    exit 1
fi

# =============================================================================
# PASSO 3: INICIALIZAR BANCO DE DADOS
# =============================================================================
echo ""
echo "🗄️ Passo 3: Inicializando Banco de Dados..."
echo ""
python init_taskflowai.py full

if [ $? -eq 0 ]; then
    echo "✅ Banco de dados inicializado com sucesso!"
else
    echo "❌ Erro ao inicializar banco de dados"
    exit 1
fi

# =============================================================================
# PASSO 4: CORRIGIR TEMPLATES (OPCIONAL)
# =============================================================================
echo ""
echo "🔧 Passo 4: Corrigir Templates? (opcional)"
read -p "Deseja executar fix_templates_paths.py? (s/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    python fix_templates_paths.py
    echo "✅ Templates corrigidos!"
fi

# =============================================================================
# PASSO 5: VERIFICAR STATUS
# =============================================================================
echo ""
echo "📊 Passo 5: Verificando Status do Sistema..."
echo ""
python init_taskflowai.py status

# =============================================================================
# FINALIZAÇÃO
# =============================================================================
echo ""
echo "=========================================="
echo "✅ Deploy Concluído!"
echo "=========================================="
echo ""
echo "🌐 Próximos passos:"
echo "1. Vá para a aba Web no PythonAnywhere"
echo "2. Clique em 'Reload lobtechsolutions.pythonanywhere.com'"
echo "3. Teste o sistema em: https://lobtechsolutions.pythonanywhere.com/taskflowai/"
echo ""
echo "👤 Credenciais Admin:"
echo "   Username: thiagolobo"
echo "   Password: #Wolf@1902"
echo ""
echo "🔍 Verificar funcionamento:"
echo "   Health Check: https://lobtechsolutions.pythonanywhere.com/taskflowai/health"
echo "   Login: https://lobtechsolutions.pythonanywhere.com/taskflowai/login"
echo ""
echo "📚 Documentação completa: DEPLOY_PYTHONANYWHERE.md"
echo ""
