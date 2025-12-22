#!/bin/bash
# =============================================================================
# COMANDOS PRONTOS PARA DEPLOY NO PYTHONANYWHERE
# =============================================================================
# Cole estes comandos diretamente no console Bash do PythonAnywhere
# https://www.pythonanywhere.com/user/lobtechsolutions/consoles/
# =============================================================================

echo "🚀 Iniciando deploy do TaskFlowAI no PythonAnywhere..."
echo ""

# -----------------------------------------------------------------------------
# PASSO 1: Clonar o repositório
# -----------------------------------------------------------------------------
echo "📦 Clonando repositório do GitHub..."
cd ~
git clone https://github.com/maikonthiago/taskflowai.git TaskFlowAI
cd TaskFlowAI

# -----------------------------------------------------------------------------
# PASSO 2: Criar e ativar ambiente virtual Python 3.10
# -----------------------------------------------------------------------------
echo "🐍 Criando ambiente virtual Python 3.10..."
mkvirtualenv --python=/usr/bin/python3.10 taskflowai
workon taskflowai

# -----------------------------------------------------------------------------
# PASSO 3: Instalar dependências
# -----------------------------------------------------------------------------
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# -----------------------------------------------------------------------------
# PASSO 4: Criar arquivo .env com configurações
# -----------------------------------------------------------------------------
echo "⚙️  Criando arquivo de configuração..."
cat > .env << 'ENVFILE'
# Ambiente
FLASK_ENV=production

# Chaves Secretas (GERE NOVAS CHAVES SEGURAS!)
SECRET_KEY=MUDE_ESTA_CHAVE_SECRETA_12345678901234567890
JWT_SECRET_KEY=MUDE_ESTA_JWT_CHAVE_98765432109876543210

# Banco de Dados MySQL
# Vá em Databases -> Crie: lobtechsolutions$taskflowai
# Substitua SENHA_MYSQL pela senha do seu banco
DATABASE_URL=mysql+pymysql://lobtechsolutions:SENHA_MYSQL@lobtechsolutions.mysql.pythonanywhere-services.com/lobtechsolutions$taskflowai

# Stripe (substitua por suas chaves reais)
# Obtenha em: https://dashboard.stripe.com/apikeys
STRIPE_PUBLIC_KEY=pk_test_sua_chave_publica_aqui
STRIPE_SECRET_KEY=sk_test_sua_chave_secreta_aqui
STRIPE_WEBHOOK_SECRET=whsec_sua_chave_webhook_aqui

# OpenAI (opcional - para funcionalidades de IA)
# Obtenha em: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-sua_chave_openai_aqui

# Email (opcional - para notificações)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app
ENVFILE

echo "✅ Arquivo .env criado!"
echo "⚠️  IMPORTANTE: Edite o arquivo .env e configure suas chaves:"
echo "   nano .env"
echo ""

# -----------------------------------------------------------------------------
# PASSO 5: Inicializar banco de dados
# -----------------------------------------------------------------------------
echo "🗄️  Inicializando banco de dados..."
echo "⚠️  Certifique-se de ter criado o banco MySQL primeiro!"
echo "   1. Vá em Databases no PythonAnywhere"
echo "   2. Crie um banco: lobtechsolutions\$taskflowai"
echo "   3. Anote a senha"
echo "   4. Atualize DATABASE_URL no .env"
echo ""
echo "Pressione ENTER para continuar (ou Ctrl+C para parar e configurar)..."
read

python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Banco de dados criado com sucesso!')"

# -----------------------------------------------------------------------------
# PASSO 6: Criar usuário admin
# -----------------------------------------------------------------------------
echo "👤 Criando usuário administrador..."
python create_admin.py

# -----------------------------------------------------------------------------
# PASSO 7: Instruções para configurar Web App
# -----------------------------------------------------------------------------
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ DEPLOY CONCLUÍDO NO CONSOLE!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📋 PRÓXIMOS PASSOS (no Dashboard do PythonAnywhere):"
echo ""
echo "1️⃣  Vá para a aba 'Web' (https://www.pythonanywhere.com/user/lobtechsolutions/webapps/)"
echo ""
echo "2️⃣  Configure o arquivo WSGI:"
echo "   - Clique em 'WSGI configuration file'"
echo "   - APAGUE todo o conteúdo"
echo "   - Cole o seguinte código:"
echo ""
echo "───────────────────────────────────────────────────────────────"
cat << 'WSGICODE'
import sys
import os

# Adicionar o diretório do projeto ao path
project_folder = '/home/lobtechsolutions/TaskFlowAI'
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

# Carregar variáveis de ambiente do .env
from dotenv import load_dotenv
project_env = os.path.join(project_folder, '.env')
load_dotenv(project_env)

# Importar a aplicação Flask
from app import app as application
WSGICODE
echo "───────────────────────────────────────────────────────────────"
echo ""
echo "3️⃣  Configure Virtualenv:"
echo "   - Clique em 'Virtualenv'"
echo "   - Digite: /home/lobtechsolutions/.virtualenvs/taskflowai"
echo ""
echo "4️⃣  Configure Static Files:"
echo "   - Clique em 'Static files'"
echo "   - Adicione:"
echo "     URL: /static/"
echo "     Directory: /home/lobtechsolutions/TaskFlowAI/static"
echo ""
echo "5️⃣  Clique no botão verde 'Reload' no topo da página"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "🌐 URLs do seu site:"
echo "   • Homepage: https://lobtechsolutions.pythonanywhere.com/"
echo "   • Login: https://lobtechsolutions.pythonanywhere.com/login"
echo "   • Dashboard: https://lobtechsolutions.pythonanywhere.com/dashboard"
echo ""
echo "🔐 Credenciais Admin:"
echo "   • Usuário: thiagolobo"
echo "   • Senha: #Wolf@1902"
echo ""
echo "📖 Documentação completa:"
echo "   • INSTRUCOES_FINAIS.md"
echo "   • DEPLOY.md"
echo "   • README.md"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  🎉 TaskFlowAI instalado com sucesso!"
echo "════════════════════════════════════════════════════════════════"
