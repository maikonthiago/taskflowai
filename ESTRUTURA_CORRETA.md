# 🔍 Análise da Estrutura do Projeto

## ❌ PROBLEMA IDENTIFICADO

Você tem **DUAS estruturas duplicadas** no projeto:

```
TaskFlowAI/                          ← RAIZ (arquivos duplicados)
├── app.py                           ← DUPLICADO
├── models.py                        ← DUPLICADO
├── config.py                        ← DUPLICADO
├── static/                          ← PASTA PRINCIPAL (com avatars, uploads, images)
│   ├── css/
│   ├── js/
│   ├── avatars/                     ← Usado pelo sistema
│   ├── uploads/                     ← Usado pelo sistema
│   └── images/
├── templates/                       ← TEMPLATES PRINCIPAIS
│   ├── base.html
│   ├── dashboard.html
│   └── ...
├── frontend/                        ← ESTRUTURA ANTIGA (não usada)
│   ├── static/
│   └── templates/
└── taskflowai/                      ← SUBPASTA DUPLICADA
    ├── app.py                       ← DUPLICADO
    ├── models.py                    ← DUPLICADO
    ├── config.py                    ← DUPLICADO
    ├── static/                      ← DUPLICADO
    ├── templates/                   ← DUPLICADO
    └── frontend/                    ← DUPLICADO
```

---

## ✅ ESTRUTURA CORRETA PARA USAR

O **app.py** usa diretamente as pastas **na raiz do projeto**:

```python
# Linha 33 do app.py:
app = Flask(__name__)  # ← Flask procura templates/ e static/ na MESMA pasta do app.py
```

O Flask, por padrão, procura:
- `templates/` → No mesmo diretório do `app.py`
- `static/` → No mesmo diretório do `app.py`

---

## 📂 ESTRUTURA REAL QUE O SISTEMA USA

```
/home/lobtechsolutions/TaskFlowAI/taskflowai/
├── app.py                           ← Arquivo principal
├── models.py                        ← Modelos do banco
├── config.py                        ← Configurações
├── static/                          ← ✅ ESTA é a pasta usada pelo Flask
│   ├── css/
│   │   └── main.css
│   ├── js/
│   │   └── main.js
│   ├── avatars/                     ← Upload de avatares
│   ├── uploads/                     ← Upload de arquivos
│   └── images/                      ← Imagens do sistema
├── templates/                       ← ✅ ESTA é a pasta usada pelo Flask
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── landing.html
│   └── ...
└── taskflowai.db                    ← Banco de dados
```

---

## 🗑️ PASTAS QUE PODEM SER REMOVIDAS

### 1. Pasta `frontend/` (não é usada)
```bash
rm -rf /home/lobtechsolutions/TaskFlowAI/taskflowai/frontend/
```

**Por quê?** O Flask já usa `static/` e `templates/` diretamente. A pasta `frontend/` é redundante.

### 2. Arquivos duplicados na raiz
Se você tem arquivos na raiz de `TaskFlowAI/` e também em `TaskFlowAI/taskflowai/`, mantenha apenas os de `taskflowai/`.

---

## 🔧 PATH CORRETO NO WSGI

O WSGI deve apontar para:

```python
taskflowai_path = '/home/lobtechsolutions/TaskFlowAI/taskflowai'
```

E o static files no PythonAnywhere:

```
URL: /taskflowai/static/
Directory: /home/lobtechsolutions/TaskFlowAI/taskflowai/static
```

---

## 📊 COMPARAÇÃO: FRONTEND vs RAIZ

### ❌ Estrutura `frontend/` (NÃO USADA):
```
frontend/
├── static/
│   ├── css/style.css              ← Arquivo diferente
│   └── js/main.js
└── templates/
    ├── base.html
    ├── dashboard.html
    └── ...
```

### ✅ Estrutura na RAIZ (USADA PELO FLASK):
```
static/
├── css/main.css                    ← Arquivo usado
├── js/main.js
├── avatars/                        ← Funcionalidades do sistema
├── uploads/                        ← Funcionalidades do sistema
└── images/
```

---

## 🎯 CONCLUSÃO

### O sistema usa:
- ✅ `TaskFlowAI/taskflowai/static/` ← **ESTA pasta**
- ✅ `TaskFlowAI/taskflowai/templates/` ← **ESTA pasta**

### Não usa:
- ❌ `TaskFlowAI/taskflowai/frontend/static/`
- ❌ `TaskFlowAI/taskflowai/frontend/templates/`

### Path correto para PythonAnywhere:
```
/home/lobtechsolutions/TaskFlowAI/taskflowai
```

---

## 🚀 AÇÕES RECOMENDADAS

1. **Manter estrutura atual** (já está correta em `taskflowai/`)
2. **Remover pasta `frontend/`** (não é usada)
3. **Configurar WSGI** para `/home/lobtechsolutions/TaskFlowAI/taskflowai`
4. **Configurar static files** para `/home/lobtechsolutions/TaskFlowAI/taskflowai/static`

---

*Atualizado: 29/12/2025*
