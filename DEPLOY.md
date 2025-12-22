# TaskFlowAI - Deploy no PythonAnywhere

## Instruções de Deploy

### 1. Preparar ambiente local

```bash
# Criar repositório Git
cd /home/thiagolobopersonaltrainer/TaskFlowAI
git init
git add .
git commit -m "Initial commit: TaskFlowAI complete system"
git remote add origin https://github.com/maikonthiago/taskflowai.git
git push -u origin main
```

### 2. No PythonAnywhere

#### 2.1 Clonar repositório

```bash
cd ~
git clone https://github.com/maikonthiago/taskflowai.git TaskFlowAI
cd TaskFlowAI
```

#### 2.2 Criar ambiente virtual

```bash
mkvirtualenv --python=/usr/bin/python3.10 taskflowai
workon taskflowai
pip install -r requirements.txt
```

#### 2.3 Configurar variáveis de ambiente

Criar arquivo `.env`:

```bash
nano .env
```

Adicionar:

```
FLASK_ENV=production
SECRET_KEY=gere-uma-chave-secreta-forte-aqui
JWT_SECRET_KEY=gere-outra-chave-secreta-aqui

# Database (MySQL do PythonAnywhere)
DATABASE_URL=mysql+pymysql://lobtechsolutions:SENHA@lobtechsolutions.mysql.pythonanywhere-services.com/lobtechsolutions$lobtechsolutionstaskflowai

# Stripe (suas chaves)
STRIPE_PUBLIC_KEY=pk_live_sua_chave
STRIPE_SECRET_KEY=sk_live_sua_chave
STRIPE_WEBHOOK_SECRET=whsec_sua_chave

# OpenAI (opcional)
OPENAI_API_KEY=sk-sua-chave
```

#### 2.4 Inicializar banco de dados

```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
python create_admin.py
```

#### 2.5 Configurar WSGI

No PythonAnywhere Web tab, criar arquivo WSGI (`/var/www/lobtechsolutions_pythonanywhere_com_wsgi.py`):

```python
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
```

#### 2.6 Configurar Static Files

Na aba Web do PythonAnywhere:

| URL | Directory |
|-----|-----------|
| /static/ | /home/lobtechsolutions/TaskFlowAI/static |

#### 2.7 Configurar Subpath (se necessário)

Para rodar em `lobtechsolutions.com.br/taskflowai`:

Modificar `app.py` para adicionar:

```python
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

def simple_app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [b'Default Application']

app.wsgi_app = DispatcherMiddleware(simple_app, {
    '/taskflowai': app.wsgi_app
})
```

### 3. Configurar Banco MySQL

No PythonAnywhere:
1. Databases tab
2. Banco criado: `lobtechsolutions$lobtechsolutionstaskflowai`
3. Anotar senha
4. Atualizar `.env` com credenciais

### 4. Configurar Tarefas Agendadas (opcional)

Para limpeza, backups etc:

```bash
# Adicionar em Scheduled tasks
# Diariamente às 3AM
cd /home/lobtechsolutions/TaskFlowAI && /home/lobtechsolutions/.virtualenvs/taskflowai/bin/python cleanup.py
```

### 5. Domínio Personalizado

1. No PythonAnywhere Web tab
2. Add new web app
3. Manual configuration
4. Domain: lobtechsolutions.com.br

Configurar DNS:
```
A record: lobtechsolutions.com.br → IP do PythonAnywhere
CNAME: www.lobtechsolutions.com.br → lobtechsolutions.pythonanywhere.com
```

### 6. SSL/HTTPS

No PythonAnywhere Web tab:
- Force HTTPS: ✓

### 7. Reload

Após qualquer mudança:

```bash
# Via console
touch /var/www/lobtechsolutions_pythonanywhere_com_wsgi.py

# Ou clicar em "Reload" no Web tab
```

### 8. Logs

Verificar logs em:
- Error log: `/var/log/lobtechsolutions.pythonanywhere.com.error.log`
- Server log: `/var/log/lobtechsolutions.pythonanywhere.com.server.log`

### 9. Manutenção

```bash
# Atualizar código
cd ~/TaskFlowAI
git pull origin main
workon taskflowai
pip install -r requirements.txt
touch /var/www/lobtechsolutions_pythonanywhere_com_wsgi.py
```

### 10. Backup

```bash
# Backup do banco
mysqldump -u lobtechsolutions -p lobtechsolutions$lobtechsolutionstaskflowai > backup.sql

# Backup dos arquivos
tar -czf taskflowai_backup.tar.gz ~/TaskFlowAI
```

## Troubleshooting

### Erro 502 Bad Gateway
- Verificar logs de erro
- Verificar se virtualenv está correto
- Verificar imports no WSGI

### Banco de dados não conecta
- Verificar credenciais no `.env`
- Verificar se banco foi criado
- Testar conexão manual

### Static files não carregam
- Verificar configuração de Static Files
- Verificar permissões dos arquivos
- Fazer reload da aplicação

## URLs Importantes

- **Site:** https://www.lobtechsolutions.com.br/
- **Dashboard:** https://www.lobtechsolutions.com.br/dashboard
- **Admin:** https://www.lobtechsolutions.com.br/login
  - User: thiagolobo
  - Pass: #Wolf@1902

## Suporte

Para problemas, verificar:
1. Logs de erro do PythonAnywhere
2. Console do PythonAnywhere
3. Fórum PythonAnywhere
4. Documentação TaskFlowAI
