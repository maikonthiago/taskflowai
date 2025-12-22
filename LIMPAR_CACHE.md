# 🚀 COMANDOS PARA ATUALIZAR E LIMPAR CACHE - PYTHONANYWHERE

## ⚡ Atualizar Código e Limpar Cache

Execute estes comandos NO CONSOLE BASH do PythonAnywhere:

```bash
# 1. Ir para o diretório
cd ~/TaskFlowAI

# 2. Atualizar código
git fetch origin
git reset --hard origin/main

# 3. Limpar cache Python (arquivos .pyc)
find . -type f -name '*.pyc' -delete
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null

# 4. Recarregar ambiente virtual
workon taskflowai
pip install --upgrade -r requirements.txt
```

## 🔄 Após Executar os Comandos Acima

1. Vá para: **Web** tab no PythonAnywhere
2. Clique no botão verde: **"Reload lobtechsolutions.pythonanywhere.com"**
3. Aguarde 5 segundos
4. Teste: https://lobtechsolutions.pythonanywhere.com/taskflowai/login

## 🧹 Se Ainda Não Funcionar - Limpeza Completa

```bash
# No console Bash do PythonAnywhere:

cd ~/TaskFlowAI

# Remover ambiente virtual e recriar
rmvirtualenv taskflowai
mkvirtualenv --python=/usr/bin/python3.10 taskflowai
workon taskflowai
pip install -r requirements.txt

# Forçar reload
touch /var/www/lobtechsolutions_pythonanywhere_com_wsgi.py
```

Depois **Reload** no Web tab novamente.

## 🌐 Limpar Cache do Navegador

No navegador:
- **Chrome/Edge**: `Ctrl + Shift + Delete` → Limpar cache
- **Firefox**: `Ctrl + Shift + Delete` → Limpar cache
- Ou fazer **Hard Reload**: `Ctrl + Shift + R`

## ✅ O Que Foi Corrigido Agora

Todos os `url_for()` foram substituídos por caminhos absolutos:

- ❌ `redirect(url_for('dashboard'))` 
- ✅ `redirect('/taskflowai/dashboard')`

Isso garante que SEMPRE redirecione para o caminho correto!

## 📝 Verificar se Funcionou

1. Acesse: https://lobtechsolutions.pythonanywhere.com/taskflowai/login
2. Faça login: `thiagolobo` / `#Wolf@1902`
3. Deve redirecionar para: https://lobtechsolutions.pythonanywhere.com/taskflowai/dashboard

Se continuar errando, veja os logs:
```bash
tail -30 /var/log/lobtechsolutions.pythonanywhere.com.error.log
```
