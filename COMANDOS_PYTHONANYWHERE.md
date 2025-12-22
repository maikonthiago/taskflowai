# 🚀 COMANDOS RÁPIDOS - TASKFLOWAI NO PYTHONANYWHERE

## ✅ Setup Inicial (já feito)
```bash
cd ~/TaskFlowAI
workon taskflowai
pip install -r requirements.txt
```

## 📊 Inicializar Banco de Dados

### ⚠️ IMPORTANTE: Corrigir DATABASE_URL Primeiro!

Se a senha do MySQL tiver caracteres especiais (`#`, `@`, `!`, etc.), você precisa fazer URL encoding:

```bash
cd ~/TaskFlowAI
workon taskflowai
python fix_database_url.py
```

Siga as instruções e atualize o arquivo `.env` com a URL gerada.

**Exemplo:** Se a senha é `#Wolf@1902`, a URL encoded será: `%23Wolf%401902`

### Método 1: Usando o script Python (RECOMENDADO)
```bash
cd ~/TaskFlowAI
workon taskflowai
python init_db.py
```

### Método 2: Usando python -c com aspas simples (evita problema com !)
```bash
cd ~/TaskFlowAI
workon taskflowai
python -c 'from app import app, db; app.app_context().push(); db.create_all(); print("Banco inicializado")'
```

## 👤 Criar Usuário Admin
```bash
cd ~/TaskFlowAI
workon taskflowai
python create_admin.py
```

## 🔧 Configuração do WSGI

1. **Cole o conteúdo do arquivo** `lobtechsolutions_pythonanywhere_com_wsgi.py` no arquivo WSGI do PythonAnywhere:
   - Vá em: **Web** → **WSGI configuration file**
   - Caminho: `/var/www/lobtechsolutions_pythonanywhere_com_wsgi.py`
   - Cole TODO o conteúdo do arquivo `lobtechsolutions_pythonanywhere_com_wsgi.py` que está no repositório

2. **Salve** e clique em **Reload** no Web tab

## 📁 Configuração de Static Files (já feito)

No Web tab do PythonAnywhere, adicione:

| URL | Directory |
|-----|-----------|
| /taskflowai/static/ | /home/lobtechsolutions/TaskFlowAI/static |

## 🧪 Testar a Aplicação

### Health Check
```bash
curl https://lobtechsolutions.pythonanywhere.com/taskflowai/health
```

### Acessar no Navegador
- Landing Page: https://lobtechsolutions.pythonanywhere.com/taskflowai/
- Login: https://lobtechsolutions.pythonanywhere.com/taskflowai/login
- Dashboard: https://lobtechsolutions.pythonanywhere.com/taskflowai/dashboard

## 🔐 Credenciais Admin
- **Usuário:** thiagolobo
- **Senha:** #Wolf@1902

## 🐛 Troubleshooting

### Ver logs de erro
```bash
# No PythonAnywhere, vá em:
# Web → Log files → Error log
tail -f /var/log/lobtechsolutions.pythonanywhere.com.error.log
```

### Testar conexão com banco
```bash
cd ~/TaskFlowAI
workon taskflowai
python -c 'from app import db; print(db.engine.url)'
```

### Verificar se tabelas foram criadas
```bash
cd ~/TaskFlowAI
workon taskflowai
python -c 'from app import app, db; from sqlalchemy import inspect; app.app_context().push(); inspector = inspect(db.engine); print(inspector.get_table_names())'
```

### Recarregar aplicação
Vá em: **Web** → Botão verde **Reload lobtechsolutions.pythonanywhere.com**

## 📝 Checklist Final

- [ ] Banco de dados inicializado (`python init_db.py`)
- [ ] Admin criado (`python create_admin.py`)
- [ ] Arquivo WSGI atualizado (copiado `lobtechsolutions_pythonanywhere_com_wsgi.py`)
- [ ] Static files configurado (`/taskflowai/static/` → `/home/lobtechsolutions/TaskFlowAI/static`)
- [ ] Reload feito no Web tab
- [ ] Health check respondendo
- [ ] Login funcionando

## 🎉 Pronto!

Acesse: **https://lobtechsolutions.pythonanywhere.com/taskflowai/**
