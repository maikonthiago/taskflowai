# 🚀 TaskFlowAI - Guia de Deploy no PythonAnywhere

Este documento contém todas as instruções para fazer o deploy do TaskFlowAI no PythonAnywhere, integrado ao sistema existente.

## 📋 Pré-requisitos

- Conta no PythonAnywhere
- Sistema portfólio já funcionando em `/home/lobtechsolutions/lobtech-briefing-system`
- Acesso ao arquivo WSGI principal: `lobtechsolutions_pythonanywhere_com_wsgi.py`

---

## 📦 1. Upload dos Arquivos

### 1.1 Estrutura de Diretórios

Faça upload de todos os arquivos do TaskFlowAI para:

```
/home/lobtechsolutions/TaskFlowAI/taskflowai/
```

A estrutura deve ficar:

```
/home/lobtechsolutions/TaskFlowAI/taskflowai/
├── app.py
├── models.py
├── config.py
├── ai_service.py
├── stripe_payment.py
├── init_taskflowai.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── landing.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── workspace.html
│   ├── project.html
│   ├── tasks.html
│   ├── task.html
│   ├── kanban.html
│   ├── calendar.html
│   ├── chat.html
│   ├── documents.html
│   ├── settings.html
│   ├── subscription.html
│   ├── pricing.html
│   ├── admin_dashboard.html
│   ├── 404.html
│   └── 500.html
└── static/
    ├── css/
    │   └── main.css
    └── js/
        └── main.js
```

---

## 🔧 2. Configurar Virtual Environment

### 2.1 Criar Virtual Environment

```bash
cd /home/lobtechsolutions
mkvirtualenv taskflowai --python=python3.10
```

### 2.2 Ativar o Ambiente

```bash
workon taskflowai
```

### 2.3 Instalar Dependências

```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
pip install -r requirements.txt
```

### 2.4 Verificar Instalação

```bash
pip list
```

Pacotes essenciais que devem estar instalados:
- Flask
- Flask-SQLAlchemy
- Flask-Login
- Flask-JWT-Extended
- Flask-SocketIO
- Flask-CORS
- python-dotenv
- Werkzeug

---

## 🗄️ 3. Inicializar Banco de Dados

### 3.1 Executar Script de Inicialização

```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
workon taskflowai
python init_taskflowai.py full
```

Este comando irá:
- ✅ Criar todas as tabelas do banco de dados
- ✅ Inserir dados padrão (planos de assinatura, configurações)
- ✅ Criar usuário administrador
- ✅ Criar workspace padrão

### 3.2 Credenciais do Admin

Após a inicialização, use estas credenciais para acessar:

```
Username: thiagolobo
Email: thiago@taskflowai.com
Password: #Wolf@1902
```

### 3.3 Verificar Status

```bash
python init_taskflowai.py status
```

---

## 🌐 4. Configurar WSGI

### 4.1 O WSGI já foi atualizado

O arquivo `lobtechsolutions_pythonanywhere_com_wsgi.py` já foi atualizado para incluir o TaskFlowAI.

A seção do TaskFlowAI foi adicionada ao final, seguindo o mesmo padrão dos outros sistemas:

```python
# ==========================================
# SISTEMA TASKFLOWAI - /taskflowai
# ==========================================
```

### 4.2 Estrutura do WSGI

O TaskFlowAI está configurado para rodar em **`/taskflowai`** com:

- ✅ Cache de aplicação (evita recriar app a cada requisição)
- ✅ Isolamento de módulos (evita conflitos com outros sistemas)
- ✅ Roteamento correto para todas as rotas
- ✅ Health check em `/taskflowai/health`

### 4.3 Rotas Disponíveis

Após o deploy, o sistema estará disponível em:

```
https://lobtechsolutions.pythonanywhere.com/taskflowai/
```

**Rotas principais:**
- `/taskflowai/` - Landing page
- `/taskflowai/login` - Login
- `/taskflowai/register` - Registro
- `/taskflowai/dashboard` - Dashboard (requer login)
- `/taskflowai/pricing` - Planos de assinatura
- `/taskflowai/admin/console` - Painel administrativo
- `/taskflowai/health` - Health check da aplicação

**APIs:**
- `/taskflowai/api/workspaces` - Gerenciar workspaces
- `/taskflowai/api/projects` - Gerenciar projetos
- `/taskflowai/api/tasks` - Gerenciar tarefas
- `/taskflowai/api/notifications` - Notificações
- `/taskflowai/api/ai/generate-tasks` - Gerar tarefas com IA

---

## 🔐 5. Configurar Variáveis de Ambiente (Opcional)

### 5.1 Criar arquivo .env

Se quiser usar variáveis de ambiente (recomendado para produção):

```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
nano .env
```

### 5.2 Adicionar Configurações

```bash
# Flask
FLASK_ENV=production
SECRET_KEY=seu-secret-key-super-seguro-aqui
JWT_SECRET_KEY=seu-jwt-secret-key-aqui

# Database
DATABASE_URL=sqlite:///taskflowai.db

# OpenAI (para recursos de IA)
OPENAI_API_KEY=sua-chave-openai-aqui

# Stripe (para pagamentos)
STRIPE_PUBLIC_KEY=sua-chave-publica-stripe
STRIPE_SECRET_KEY=sua-chave-secreta-stripe
STRIPE_WEBHOOK_SECRET=seu-webhook-secret
```

**Nota:** As configurações também podem ser gerenciadas pelo painel administrativo em `/taskflowai/admin/console`.

---

## 🔄 6. Reiniciar Aplicação

### 6.1 No PythonAnywhere Dashboard

1. Vá para a aba **Web**
2. Clique em **Reload lobtechsolutions.pythonanywhere.com**
3. Aguarde o reload completar

### 6.2 Verificar Logs

Se houver algum erro, verifique os logs:

1. Clique em **Log files**
2. Abra **Error log**
3. Verifique mensagens de erro

---

## ✅ 7. Testar Sistema

### 7.1 Health Check

Acesse no navegador:
```
https://lobtechsolutions.pythonanywhere.com/taskflowai/health
```

Resposta esperada:
```json
{
  "status": "ok",
  "app": "TaskFlowAI",
  "version": "1.0.0"
}
```

### 7.2 Landing Page

Acesse:
```
https://lobtechsolutions.pythonanywhere.com/taskflowai/
```

Deve mostrar a página inicial do TaskFlowAI.

### 7.3 Login

1. Acesse: `https://lobtechsolutions.pythonanywhere.com/taskflowai/login`
2. Use as credenciais do admin:
   - Username: `thiagolobo`
   - Password: `#Wolf@1902`
3. Deve redirecionar para o dashboard

### 7.4 Painel Admin

Após fazer login como admin, acesse:
```
https://lobtechsolutions.pythonanywhere.com/taskflowai/admin/console
```

Deve mostrar:
- Estatísticas de usuários
- Planos de assinatura
- Configurações do sistema

---

## 🎨 8. Templates e Assets

### 8.1 Verificar CSS/JS

Os arquivos estáticos devem estar em:
```
/home/lobtechsolutions/TaskFlowAI/taskflowai/static/
```

### 8.2 Verificar Templates

Os templates devem estar em:
```
/home/lobtechsolutions/TaskFlowAI/taskflowai/templates/
```

### 8.3 Ajustar Links nos Templates

**IMPORTANTE:** Todos os links nos templates devem incluir o prefixo `/taskflowai`:

❌ **Errado:**
```html
<a href="/dashboard">Dashboard</a>
<link rel="stylesheet" href="/static/css/main.css">
```

✅ **Correto:**
```html
<a href="/taskflowai/dashboard">Dashboard</a>
<link rel="stylesheet" href="/taskflowai/static/css/main.css">
```

Ou use `url_for`:
```html
<a href="{{ url_for('dashboard') }}">Dashboard</a>
```

---

## 🐛 9. Troubleshooting

### 9.1 Erro 404 nas Rotas

**Problema:** Rotas retornando 404

**Solução:**
- Verifique se o WSGI está configurado corretamente
- Certifique-se de que está acessando com o prefixo `/taskflowai`
- Reinicie a aplicação web

### 9.2 Erro de Import

**Problema:** `ModuleNotFoundError` ou `ImportError`

**Solução:**
```bash
workon taskflowai
pip install -r requirements.txt
```

### 9.3 Banco de Dados não Inicializado

**Problema:** Tabelas não existem

**Solução:**
```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
workon taskflowai
python init_taskflowai.py full
```

### 9.4 Conflito de Módulos

**Problema:** Erro relacionado a conflito entre sistemas

**Solução:** O WSGI já está configurado com isolamento de módulos. Se persistir:
- Verifique se o cache está funcionando (`_taskflowai_app_cache`)
- Reinicie a aplicação web

### 9.5 Arquivos Estáticos não Carregam

**Problema:** CSS/JS não aparecem

**Solução:**
1. Verifique se os arquivos existem em `/static/`
2. Verifique os caminhos nos templates
3. Certifique-se de usar `/taskflowai/static/...`

---

## 🚦 10. Manutenção

### 10.1 Backup do Banco de Dados

```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
cp taskflowai.db taskflowai.db.backup-$(date +%Y%m%d)
```

### 10.2 Atualizar Sistema

Após fazer alterações no código:

```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
git pull  # Se estiver usando git
```

Depois, no PythonAnywhere:
1. Vá para aba **Web**
2. Clique em **Reload**

### 10.3 Logs

Verificar logs de erro:
```bash
tail -f /var/log/lobtechsolutions.pythonanywhere.com.error.log
```

### 10.4 Criar Novos Admins

```bash
cd /home/lobtechsolutions/TaskFlowAI/taskflowai
workon taskflowai
python init_taskflowai.py admin
```

---

## 📊 11. Recursos do Sistema

### 11.1 Funcionalidades Principais

✅ **Gestão de Workspaces**
- Criar, editar e deletar workspaces
- Convidar membros
- Definir permissões

✅ **Projetos e Tarefas**
- Criar projetos dentro de workspaces
- Gerenciar tarefas com status, prioridade, datas
- Atribuir tarefas a membros
- Comentários e anexos

✅ **Visualizações**
- Lista de tarefas
- Kanban board
- Calendário
- Dashboard com estatísticas

✅ **Inteligência Artificial**
- Gerar tarefas automaticamente a partir de descrições
- Sugestões inteligentes

✅ **Sistema de Assinatura**
- Planos: Free, Pro, Business
- Integração com Stripe (configurável)

✅ **Painel Administrativo**
- Gerenciar usuários
- Configurar planos
- Ajustar configurações do sistema
- Visualizar estatísticas

### 11.2 Limites por Plano

**Free:**
- 1 workspace
- 3 projetos
- 100 tarefas
- 3 membros
- 100 MB storage
- 10 requisições IA/mês

**Pro (R$ 29,90/mês):**
- 5 workspaces
- Projetos ilimitados
- Tarefas ilimitadas
- 20 membros
- 10 GB storage
- 500 requisições IA/mês

**Business (R$ 79,90/mês):**
- Workspaces ilimitados
- Projetos ilimitados
- Tarefas ilimitadas
- Membros ilimitados
- 100 GB storage
- IA ilimitada

---

## 🎯 12. Próximos Passos

Após o deploy bem-sucedido:

1. ✅ **Testar todas as funcionalidades**
   - Criar workspace
   - Criar projeto
   - Criar tarefas
   - Testar IA (se configurado)

2. ✅ **Personalizar**
   - Ajustar cores e branding nos templates
   - Configurar planos de assinatura
   - Adicionar logo/favicon

3. ✅ **Configurar Integrações**
   - OpenAI para IA (opcional)
   - Stripe para pagamentos (opcional)
   - Email SMTP (opcional)

4. ✅ **Segurança**
   - Trocar SECRET_KEY padrão
   - Configurar HTTPS
   - Revisar permissões

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs de erro
2. Execute `python init_taskflowai.py status` para diagnóstico
3. Revise este guia
4. Verifique o WSGI está correto

---

## ✨ Conclusão

Seu TaskFlowAI agora está rodando em:

🌐 **URL:** https://lobtechsolutions.pythonanywhere.com/taskflowai/

👤 **Admin:**
- Username: `thiagolobo`
- Password: `#Wolf@1902`

🚀 **Pronto para uso!**

---

*Última atualização: Dezembro 2025*
