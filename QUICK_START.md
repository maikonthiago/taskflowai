# ⚡ TaskFlowAI - Guia Rápido de Deploy

## 🎯 Para Começar Agora

### 1️⃣ Criar Ambiente (5 min)
```bash
cd /home/lobtechsolutions
mkvirtualenv taskflowai --python=python3.10
workon taskflowai
```

### 2️⃣ Instalar (2 min)
```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
pip install -r requirements.txt
```

### 3️⃣ Inicializar (1 min)
```bash
python init_taskflowai.py full
```
**Resultado:** ✅ Banco criado + Admin criado

### 4️⃣ Reload (1 min)
- PythonAnywhere → Aba **Web** → **Reload**

### 5️⃣ Testar
```
🌐 https://lobtechsolutions.pythonanywhere.com/taskflowai/
👤 thiagolobo / #Wolf@1902
```

---

## 📁 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| **RESUMO_SISTEMA.md** | 📋 Visão geral completa do sistema |
| **DEPLOY_PYTHONANYWHERE.md** | 📚 Guia detalhado passo a passo |
| **CHECKLIST_DEPLOY.md** | ✅ Checklist de verificação |
| **init_taskflowai.py** | 🔧 Script de inicialização |
| **fix_templates_paths.py** | 🎨 Correção de templates |
| **deploy_quick.sh** | ⚡ Script automático |

---

## 🔍 Verificações Rápidas

### Health Check
```bash
curl https://lobtechsolutions.pythonanywhere.com/taskflowai/health
# Esperado: {"status":"ok","app":"TaskFlowAI","version":"1.0.0"}
```

### Status Local
```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
python init_taskflowai.py status
# Mostra estatísticas do banco de dados
```

### Ver Logs
```bash
tail -f /var/log/lobtechsolutions.pythonanywhere.com.error.log
```

---

## 🚨 Problemas Comuns

### ❌ Erro 404
**Causa:** WSGI não configurado ou app não recarregado
**Solução:** 
1. Verificar se WSGI tem seção TaskFlowAI
2. Reload da aplicação web

### ❌ ModuleNotFoundError
**Causa:** Dependências não instaladas
**Solução:**
```bash
workon taskflowai
pip install -r requirements.txt
```

### ❌ Banco não existe
**Causa:** Banco não foi inicializado
**Solução:**
```bash
python init_taskflowai.py full
```

### ❌ CSS não carrega
**Causa:** Caminhos incorretos nos templates
**Solução:**
```bash
python fix_templates_paths.py
```

---

## 🎯 URLs Principais

```
Landing:      /taskflowai/
Login:        /taskflowai/login
Dashboard:    /taskflowai/dashboard
Admin:        /taskflowai/admin/console
Health:       /taskflowai/health
```

---

## 📞 Comandos Úteis

### Criar novo admin
```bash
python init_taskflowai.py admin
```

### Backup do banco
```bash
cp taskflowai.db taskflowai.db.backup
```

### Reiniciar tudo
```bash
rm taskflowai.db
python init_taskflowai.py full
# Depois: Web → Reload
```

---

## ✅ Checklist Mínimo

- [ ] Virtualenv criado e ativado
- [ ] Dependências instaladas
- [ ] `python init_taskflowai.py full` executado
- [ ] App recarregado no PythonAnywhere
- [ ] Health check funcionando
- [ ] Login com admin funcionando

---

## 📚 Mais Informações

Para guia completo, veja: **DEPLOY_PYTHONANYWHERE.md**

Para resumo técnico, veja: **RESUMO_SISTEMA.md**

---

*Tempo total estimado: ~10 minutos* ⏱️
