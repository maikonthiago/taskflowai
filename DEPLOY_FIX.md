# Fix para Deploy no PythonAnywhere

## Erro Identificado
```
IndentationError: unexpected indent at line 353: if user:
```

## Solução

### 1. No Console PythonAnywhere (Bash)

```bash
cd /home/lobtechsolutions/lobtech-briefing-system

# Backup do arquivo atual
cp app.py app.py.backup

# Forçar atualização do git (descartando mudanças locais)
git fetch origin
git reset --hard origin/main

# Verificar sintaxe Python
python3 -m py_compile app.py

# Se der erro, verificar linhas problemáticas
python3 -c "import app"
```

### 2. Alternativa: Editar Manualmente

Se o git reset não resolver, edite o arquivo diretamente:

```bash
nano app.py
```

Vá até a linha 353 e verifique se há espaços/tabs misturados ou indentação incorreta.

### 3. Reiniciar o Web App

No painel Web do PythonAnywhere:
- Clique em "Reload www.lobtechsolutions.com.br"

OU via terminal:

```bash
touch /var/www/www_lobtechsolutions_com_br_wsgi.py
```

### 4. Verificar Logs

```bash
tail -f /var/log/www.lobtechsolutions.com.br.error.log
```

## Comandos Completos em Sequência

```bash
cd /home/lobtechsolutions/lobtech-briefing-system
git fetch origin
git reset --hard origin/main
python3 -m py_compile app.py && echo "✓ Sintaxe OK" || echo "✗ Erro de sintaxe"
pip install -r requirements.txt
flask init-db
touch /var/www/www_lobtechsolutions_com_br_wsgi.py
```

## Se Ainda Houver Erro

Verifique se o WSGI está apontando para o arquivo correto:

```python
# /var/www/www_lobtechsolutions_com_br_wsgi.py deve conter:
import sys
import os

# Caminho correto do projeto
path = '/home/lobtechsolutions/lobtech-briefing-system'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```
