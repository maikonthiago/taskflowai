#!/bin/bash
# Comandos para executar no PythonAnywhere
# Cole estes comandos no console Bash do PythonAnywhere

# 1. Clonar repositório
cd ~
git clone https://github.com/maikonthiago/taskflowai.git TaskFlowAI
cd TaskFlowAI

# 2. Criar ambiente virtual Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 taskflowai

# 3. Ativar ambiente virtual
workon taskflowai

# 4. Instalar dependências
pip install -r requirements.txt

# 5. Criar arquivo .env
cat > .env << 'EOF'
FLASK_ENV=production
SECRET_KEY=GERE_UMA_CHAVE_SECRETA_FORTE_AQUI_123456789
JWT_SECRET_KEY=GERE_OUTRA_CHAVE_SECRETA_AQUI_987654321

# Database MySQL do PythonAnywhere
DATABASE_URL=mysql+pymysql://lobtechsolutions:SENHA_DO_MYSQL@lobtechsolutions.mysql.pythonanywhere-services.com/lobtechsolutions$taskflowai

# Stripe (substitua por suas chaves reais)
STRIPE_PUBLIC_KEY=pk_test_sua_chave_publica
STRIPE_SECRET_KEY=sk_test_sua_chave_secreta
STRIPE_WEBHOOK_SECRET=whsec_sua_chave_webhook

# OpenAI (opcional)
OPENAI_API_KEY=sk-sua_chave_openai
EOF

# 6. Criar banco de dados (no PythonAnywhere Dashboard):
# - Vá em "Databases"
# - Crie um banco: lobtechsolutions$taskflowai
# - Anote a senha do MySQL
# - Atualize DATABASE_URL no .env acima

# 7. Inicializar banco de dados
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Banco de dados inicializado!')"

# 8. Criar usuário admin
python create_admin.py

# 9. Configurar WSGI
# No PythonAnywhere Web tab, edite o arquivo WSGI (/var/www/lobtechsolutions_pythonanywhere_com_wsgi.py):

cat > ~/wsgi_config.py << 'EOF'
import sys
import os

# Adicionar projeto ao path
project_folder = '/home/lobtechsolutions/TaskFlowAI'
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

# Carregar variáveis de ambiente
from dotenv import load_dotenv
project_env = os.path.join(project_folder, '.env')
load_dotenv(project_env)

# Importar aplicação
from app import app as application
EOF

echo "✅ Arquivo WSGI de exemplo criado em ~/wsgi_config.py"
echo "   Cole este conteúdo no arquivo WSGI do PythonAnywhere Web tab"

# 10. Configurar arquivos estáticos no Web tab:
echo ""
echo "Configure Static Files no PythonAnywhere Web tab:"
echo "URL: /static/"
echo "Directory: /home/lobtechsolutions/TaskFlowAI/static"

# 11. Reload da aplicação
echo ""
echo "Após configurar WSGI e Static Files, clique em 'Reload' no Web tab"

echo ""
echo "✅ Setup completo!"
echo ""
echo "📝 Acesse:"
echo "   - Site: https://lobtechsolutions.pythonanywhere.com"
echo "   - Login: https://lobtechsolutions.pythonanywhere.com/login"
echo "   - Admin: thiagolobo / #Wolf@1902"
echo ""
echo "⚠️  NÃO ESQUEÇA:"
echo "   1. Configurar DATABASE_URL no .env com a senha real do MySQL"
echo "   2. Adicionar suas chaves Stripe reais"
echo "   3. Copiar conteúdo de ~/wsgi_config.py para o arquivo WSGI do PythonAnywhere"
echo "   4. Configurar Static Files"
echo "   5. Clicar em Reload"
