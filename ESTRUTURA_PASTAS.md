# 📁 ESTRUTURA DE PASTAS DO TASKFLOWAI

## ⚠️ Pastas Duplicadas Identificadas

Durante o desenvolvimento foram criadas **duas estruturas paralelas**:

### 1️⃣ Estrutura Principal (ROOT - USADO EM PRODUÇÃO)
```
/home/lobtechsolutions/TaskFlowAI/
├── app.py                    ← APP PRINCIPAL (usado pelo WSGI)
├── models.py
├── config.py
├── ai_service.py
├── stripe_payment.py
├── templates/                ← TEMPLATES USADOS ✅
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── ...
└── static/
    ├── css/
    ├── js/
    └── images/
```

### 2️⃣ Estrutura Alternativa (NÃO USADA)
```
/home/lobtechsolutions/TaskFlowAI/
├── backend/
│   └── app.py               ← APP ALTERNATIVO (não usado)
└── frontend/
    └── templates/           ← TEMPLATES ALTERNATIVOS (não usados)
        ├── base.html
        ├── landing.html
        └── dashboard.html
```

## ✅ Qual Está Sendo Usado?

O arquivo **WSGI** (`lobtechsolutions_pythonanywhere_com_wsgi.py`) carrega:
```python
os.path.join(taskflowai_path, "app.py")
```

Isso significa: **`/home/lobtechsolutions/TaskFlowAI/app.py`** (ROOT)

E o `app.py` do root usa por padrão: **`/templates`** (ROOT)

## 🔧 O Que Foi Corrigido?

✅ **Templates do ROOT** (`/templates/*.html`) - Corrigidos
✅ **Templates do FRONTEND** (`/frontend/templates/*.html`) - Corrigidos (por precaução)

Todos os links agora têm o prefixo `/taskflowai`:
- `/login` → `/taskflowai/login` ✅
- `/register` → `/taskflowai/register` ✅
- `/dashboard` → `/taskflowai/dashboard` ✅

## 📝 Arquivos Duplicados Também Encontrados

- `init_database.py` (obsoleto?)
- `init_db.py` ✅ (usado)
- `wsgi_config.py` (exemplo, não usado)

## 🚀 Comandos para Atualizar no PythonAnywhere

```bash
cd ~/TaskFlowAI
git fetch origin
git reset --hard origin/main
```

Depois clique em **Reload** no Web tab.

## 🧹 Limpeza Recomendada (Opcional)

Se quiser limpar as pastas duplicadas no futuro:

```bash
# Fazer backup primeiro
cd ~/TaskFlowAI
mkdir _backup_old_structure
mv backend/ frontend/ _backup_old_structure/
mv init_database.py wsgi_config.py _backup_old_structure/

# Commitar a limpeza
git add -A
git commit -m "Clean: Remove duplicate folders structure"
git push origin main
```

## ✅ Status Final

- ✅ Estrutura principal (ROOT) corrigida
- ✅ Links com prefixo `/taskflowai`
- ✅ Pronto para uso em produção
