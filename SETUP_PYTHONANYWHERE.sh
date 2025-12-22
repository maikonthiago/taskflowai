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
SECRET_KEY=6f4a9c0e7b8d2f1c9e3a0b7d5e8f4c2a9d1e6b8f0c3a5d7e2b4c9a8f1d6e
JWT_SECRET_KEY=9b2e7d1c8f0a6e4d5b3c9a1f7e8d2b0c4a6f5e9d1c7b8a3e2f4d0a9b6

# Database MySQL do PythonAnywhere
DATABASE_URL=mysql+pymysql://lobtechsolutions:#Wolf@1902@lobtechsolutions.mysql.pythonanywhere-services.com/lobtechsolutions$lobtechsolutionstaskflowai

# Stripe (substitua por suas chaves reais)
STRIPE_PUBLIC_KEY=pk_test_sua_chave_publica
STRIPE_SECRET_KEY=sk_test_sua_chave_secreta
STRIPE_WEBHOOK_SECRET=whsec_sua_chave_webhook

# OpenAI (opcional)
OPENAI_API_KEY=sk-sua-chave-openai-aqui
EOF

# 6. Criar banco de dados (no PythonAnywhere Dashboard):
# - Vá em "Databases"
# - Banco criado: lobtechsolutions$lobtechsolutionstaskflowai
# - Anote a senha do MySQL
# - Atualize DATABASE_URL no .env acima com a senha real

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
