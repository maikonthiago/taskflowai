# 🚀 Instruções Completas - PythonAnywhere

## 📋 1. CONFIGURAR STATIC FILES

No PythonAnywhere, vá em **Web** → **Static files** e adicione:

```
URL: /taskflowai/static/
Directory: /home/lobtechsolutions/TaskFlowAI/taskflowai/static
```

Clique em **Add a new static file mapping**.

---

## 📄 2. ATUALIZAR ARQUIVO WSGI

1. **Abra o arquivo WSGI no PythonAnywhere:**
   - Web → Code → WSGI configuration file

2. **SUBSTITUA TODO O CONTEÚDO** pelo arquivo `WSGI_PRODUCTION.py`

3. **Ou use o console:**
   ```bash
   # No console Bash do PythonAnywhere:
   cd /home/lobtechsolutions/TaskFlowAI/taskflowai
   git pull
   
   # Copiar o WSGI
   cp WSGI_PRODUCTION.py /var/www/lobtechsolutions_pythonanywhere_com_wsgi.py
   ```

---

## 🔧 3. CRIAR VIRTUAL ENVIRONMENT

```bash
# No console Bash do PythonAnywhere:
cd /home/lobtechsolutions
mkvirtualenv taskflowai --python=python3.10
```

---

## 📦 4. INSTALAR DEPENDÊNCIAS

```bash
workon taskflowai
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
pip install -r requirements.txt
```

---

## 🗄️ 5. INICIALIZAR BANCO DE DADOS

```bash
workon taskflowai
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
python init_taskflowai.py full
```

**Isso irá:**
- ✅ Criar todas as tabelas
- ✅ Inserir dados padrão (planos)
- ✅ Criar usuário admin (thiagolobo / #Wolf@1902)
- ✅ Criar workspace padrão

---

## ⚙️ 6. CONFIGURAR VIRTUALENV NO WEB

No PythonAnywhere, vá em **Web** → **Virtualenv**:

```
Path: /home/lobtechsolutions/.virtualenvs/taskflowai
```

---

## 🔄 7. RELOAD DA APLICAÇÃO

No PythonAnywhere:
- Web → **Reload lobtechsolutions.pythonanywhere.com**

---

## ✅ 8. TESTAR

### Health Check:
```
https://lobtechsolutions.pythonanywhere.com/taskflowai/health
```

**Resposta esperada:**
```json
{
  "status": "ok",
  "app": "TaskFlowAI",
  "version": "1.0.0"
}
```

### Landing Page:
```
https://lobtechsolutions.pythonanywhere.com/taskflowai/
```

### Login:
```
https://lobtechsolutions.pythonanywhere.com/taskflowai/login

Username: thiagolobo
Password: #Wolf@1902
```

---

## 📂 ESTRUTURA DE PATHS

### No Servidor:
```
/home/lobtechsolutions/TaskFlowAI/taskflowai/
├── app.py                    ← App principal
├── models.py                 ← Modelos do banco
├── config.py                 ← Configurações
├── static/                   ← CSS, JS, imagens
│   ├── css/
│   └── js/
├── templates/                ← Templates HTML
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   └── ...
└── taskflowai.db            ← Banco de dados (criado após init)
```

### Virtual Environment:
```
/home/lobtechsolutions/.virtualenvs/taskflowai/
```

---

## 🐛 TROUBLESHOOTING

### Erro 500 (Internal Server Error)

**1. Verificar logs:**
```bash
tail -100 /var/log/lobtechsolutions.pythonanywhere.com.error.log
```

**2. Verificar se banco foi criado:**
```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
ls -la taskflowai.db
```

**3. Reinicializar banco se necessário:**
```bash
workon taskflowai
python init_taskflowai.py full
```

### CSS/JS não carregam

**Verificar static files no PythonAnywhere:**
- URL deve ser: `/taskflowai/static/`
- Directory deve ser: `/home/lobtechsolutions/TaskFlowAI/taskflowai/static`

### Módulo não encontrado

**Reinstalar dependências:**
```bash
workon taskflowai
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
pip install --upgrade -r requirements.txt
```

### App não inicia

**Verificar WSGI:**
1. Arquivo deve estar em: `/var/www/lobtechsolutions_pythonanywhere_com_wsgi.py`
2. Conteúdo deve ser igual ao `WSGI_PRODUCTION.py`
3. Path do TaskFlowAI deve ser: `/home/lobtechsolutions/TaskFlowAI/taskflowai`

---

## 📊 VERIFICAR STATUS

```bash
workon taskflowai
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
python init_taskflowai.py status
```

**Saída esperada:**
```
📊 Status do TaskFlowAI
==================================================
👥 Usuários: 1 (Admin: 1)
📁 Workspaces: 1
📊 Projetos: 0
✅ Tarefas: 0
💾 Banco de dados: taskflowai.db
   Tamanho: XX.XX KB
```

---

## 🔐 CREDENCIAIS

```
Username: thiagolobo
Email: thiago@taskflowai.com
Password: #Wolf@1902
```

⚠️ **Altere a senha após primeiro login!**

---

## 📝 CHECKLIST FINAL

- [ ] Virtual environment criado (`mkvirtualenv taskflowai`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Banco inicializado (`python init_taskflowai.py full`)
- [ ] WSGI atualizado (copiar `WSGI_PRODUCTION.py`)
- [ ] Static files configurados (`/taskflowai/static/`)
- [ ] Virtualenv path configurado no Web
- [ ] App recarregado (Reload)
- [ ] Health check funcionando
- [ ] Login funcionando

---

## 🎉 PRONTO!

Se todos os passos foram seguidos, o TaskFlowAI deve estar funcionando em:

**🌐 https://lobtechsolutions.pythonanywhere.com/taskflowai/**

---

*Última atualização: Dezembro 2025*
