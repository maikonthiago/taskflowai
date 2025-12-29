# 🚀 TaskFlowAI - Índice de Documentação

> **Comece aqui!** Este é seu ponto de partida para o deploy do TaskFlowAI no PythonAnywhere.

---

## 🎯 Qual documento ler?

### 👋 Primeira vez aqui?
**→ Leia:** [RESUMO_SISTEMA.md](RESUMO_SISTEMA.md)
- Visão geral do que foi feito
- Entenda a estrutura do sistema
- Veja comandos principais

---

### ⚡ Quer fazer deploy rápido (10 min)?
**→ Siga:** [QUICK_START.md](QUICK_START.md)
- 5 passos diretos
- Comandos prontos para copiar
- Deploy em ~10 minutos

---

### 📚 Quer guia completo e detalhado?
**→ Siga:** [DEPLOY_PYTHONANYWHERE.md](DEPLOY_PYTHONANYWHERE.md)
- Passo a passo detalhado
- Explicações completas
- Troubleshooting extensivo
- Manutenção e backup

---

### ✅ Já fez deploy e quer verificar?
**→ Use:** [CHECKLIST_DEPLOY.md](CHECKLIST_DEPLOY.md)
- Lista de verificação completa
- Testes funcionais
- Configurações de segurança

---

### 📦 Quer saber quais arquivos foram criados?
**→ Veja:** [ARQUIVOS_CRIADOS.md](ARQUIVOS_CRIADOS.md)
- Lista todos os arquivos novos
- Explicação de cada arquivo
- Quando usar cada um

---

## 🔧 Comandos Principais

### Inicializar Tudo (Mais Comum)
```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
workon taskflowai
python init_taskflowai.py full
```

### Ver Status do Sistema
```bash
python init_taskflowai.py status
```

### Corrigir Paths nos Templates
```bash
python fix_templates_paths.py
```

---

## 🌐 URLs Importantes

| Recurso | URL |
|---------|-----|
| **Landing Page** | `https://lobtechsolutions.pythonanywhere.com/taskflowai/` |
| **Login** | `https://lobtechsolutions.pythonanywhere.com/taskflowai/login` |
| **Dashboard** | `https://lobtechsolutions.pythonanywhere.com/taskflowai/dashboard` |
| **Admin Console** | `https://lobtechsolutions.pythonanywhere.com/taskflowai/admin/console` |
| **Health Check** | `https://lobtechsolutions.pythonanywhere.com/taskflowai/health` |

---

## 👤 Credenciais Padrão

```
Username: thiagolobo
Password: #Wolf@1902
Email:    thiago@taskflowai.com
```

> ⚠️ **Importante:** Altere a senha após primeiro login!

---

## 📁 Estrutura de Documentação

```
📚 Documentação
├── INDEX.md                        ← VOCÊ ESTÁ AQUI
├── RESUMO_SISTEMA.md              ⭐⭐⭐ Visão geral técnica
├── QUICK_START.md                 ⭐⭐⭐ Deploy rápido
├── DEPLOY_PYTHONANYWHERE.md       ⭐⭐⭐ Guia completo
├── CHECKLIST_DEPLOY.md            ⭐⭐ Verificações
└── ARQUIVOS_CRIADOS.md            ⭐ Referência de arquivos

🔧 Scripts
├── init_taskflowai.py             ⭐⭐⭐ Inicialização
├── fix_templates_paths.py         ⭐⭐ Correção de paths
├── create_app.py                  ⭐ Factory (opcional)
└── deploy_quick.sh                ⭐ Deploy automático
```

---

## 🚦 Fluxo de Deploy

```
1. Ler Documentação
   └─→ RESUMO_SISTEMA.md ou QUICK_START.md

2. Upload dos Arquivos
   └─→ Para /home/lobtechsolutions/TaskFlowAI/taskflowai/

3. Criar Ambiente
   └─→ mkvirtualenv taskflowai --python=python3.10

4. Instalar Dependências
   └─→ pip install -r requirements.txt

5. Inicializar Sistema
   └─→ python init_taskflowai.py full

6. Reload Web App
   └─→ PythonAnywhere → Web → Reload

7. Testar
   └─→ /taskflowai/health + Login

8. Verificar
   └─→ CHECKLIST_DEPLOY.md
```

---

## ❓ FAQ Rápido

### "Por onde começo?"
→ Leia [RESUMO_SISTEMA.md](RESUMO_SISTEMA.md) primeiro

### "Quanto tempo leva?"
→ Deploy rápido: ~10 minutos | Deploy completo: ~30 minutos

### "Preciso modificar algum arquivo?"
→ Não! Tudo já está pronto. Só executar scripts.

### "O WSGI já está configurado?"
→ Sim! A seção TaskFlowAI já foi adicionada.

### "E se der erro?"
→ Veja seção Troubleshooting em [DEPLOY_PYTHONANYWHERE.md](DEPLOY_PYTHONANYWHERE.md)

### "Como verificar se funcionou?"
→ Acesse: `https://lobtechsolutions.pythonanywhere.com/taskflowai/health`

---

## ⚡ Deploy em 5 Passos

Para quem tem pressa:

```bash
# 1. Criar ambiente
mkvirtualenv taskflowai --python=python3.10

# 2. Instalar
cd /home/lobtechsolutions/TaskFlowAI/taskflowai && pip install -r requirements.txt

# 3. Inicializar
python init_taskflowai.py full

# 4. (Opcional) Corrigir templates
python fix_templates_paths.py

# 5. Reload no PythonAnywhere → Web → Reload
```

Pronto! ✅

---

## 🆘 Suporte

### Problemas?
1. Verifique logs: `/var/log/lobtechsolutions.pythonanywhere.com.error.log`
2. Execute: `python init_taskflowai.py status`
3. Consulte troubleshooting em [DEPLOY_PYTHONANYWHERE.md](DEPLOY_PYTHONANYWHERE.md)

### Dúvidas sobre arquivos?
→ Veja [ARQUIVOS_CRIADOS.md](ARQUIVOS_CRIADOS.md)

---

## ✅ Checklist Mínimo

Antes de começar, certifique-se:

- [ ] Todos os arquivos foram copiados para o servidor
- [ ] WSGI principal tem a seção TaskFlowAI
- [ ] Virtual environment está criado
- [ ] Você leu pelo menos o QUICK_START.md ou RESUMO_SISTEMA.md

---

## 🎉 Está Pronto?

**Escolha seu caminho:**

### 🏃 Rápido (10 min)
[QUICK_START.md](QUICK_START.md) → Comandos diretos

### 📖 Completo (30 min)
[DEPLOY_PYTHONANYWHERE.md](DEPLOY_PYTHONANYWHERE.md) → Guia detalhado

### 📊 Entender Primeiro
[RESUMO_SISTEMA.md](RESUMO_SISTEMA.md) → Visão geral técnica

---

## 📞 Informações Finais

**Sistema:** TaskFlowAI v1.0.0
**Deploy:** PythonAnywhere
**Subpath:** `/taskflowai`
**Python:** 3.10+
**Framework:** Flask 3.0

**Repositório:** [GitHub/TaskFlowAI](https://github.com)
**Demo:** [lobtechsolutions.pythonanywhere.com/taskflowai](https://lobtechsolutions.pythonanywhere.com/taskflowai)

---

**🚀 Boa sorte com seu deploy!**

*Se tudo correr bem, seu TaskFlowAI estará online em menos de 15 minutos!*

---

*Última atualização: Dezembro 2025*
