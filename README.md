# 🚀 TaskFlowAI

<div align="center">

**Seu fluxo de trabalho, inteligente e simples.**

Sistema completo de gerenciamento de projetos e tarefas com IA integrada, superior ao ClickUp.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[🌐 Demo](https://lobtechsolutions.pythonanywhere.com/taskflowai) • [📖 Documentação](DEPLOY_PYTHONANYWHERE.md) • [🚀 Deploy](RESUMO_SISTEMA.md)

</div>

---

## ✨ Características Principais

<table>
<tr>
<td width="50%">

### 🎯 Gestão Completa
- ✅ Workspaces, Spaces e Projetos
- ✅ Tarefas com subtarefas ilimitadas
- ✅ Multiple views: Lista, Kanban, Calendário
- ✅ Tags, prioridades e status
- ✅ Anexos e comentários
- ✅ Time tracking integrado

</td>
<td width="50%">

### 🤖 IA Integrada
- 🧠 Geração automática de tarefas
- 🧠 Estruturação de projetos
- 🧠 Resumo de reuniões
- 🧠 Análise de dados
- 🧠 Sugestão de automações
- 🧠 Assistente virtual

</td>
</tr>
<tr>
<td width="50%">

### 👥 Colaboração
- 💬 Chat em tempo real
- 🔔 Notificações instantâneas
- 📝 Documentos colaborativos
- 👤 Permissões granulares
- 📧 Convites para equipe
- 🎯 Menções e assignments

</td>
<td width="50%">

### 💳 Financeiro
- 💰 3 planos (Free, Pro, Business)
- 💳 Integração completa com Stripe
- 🎁 Trial de 14 dias grátis
- 🔒 Checkout seguro
- 📊 Portal do cliente
- ⚡ Upgrade/Downgrade automático

</td>
</tr>
</table>

---

## 🛠️ Stack Tecnológico

### Backend
```
Python 3.10+ | Flask 3.0 | SQLAlchemy | MySQL/PostgreSQL
JWT Authentication | SocketIO | Stripe API | OpenAI API
```

### Frontend
```
HTML5 | Bootstrap 5.3 | JavaScript (Vanilla) | CSS3
Responsive Design | Mobile First | Modern UI/UX
```

---

## 🚀 Instalação Rápida

### Local Development

```bash
# 1. Clone o repositório
git clone https://github.com/maikonthiago/taskflowai.git
cd taskflowai

# 2. Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure ambiente
cp .env.example .env
# Edite .env com suas configurações

# 5. Inicialize banco de dados
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# 6. Crie usuário admin
python create_admin.py

# 7. Execute servidor
python app.py
```

Acesse: http://localhost:5000

---

## ☁️ Deploy no PythonAnywhere

### Opção 1: Script Automatizado (Recomendado)

```bash
# No console do PythonAnywhere, execute:
bash <(curl -s https://raw.githubusercontent.com/maikonthiago/taskflowai/main/DEPLOY_COMMANDS.sh)
```

### Opção 2: Manual

Siga o guia completo em: [**INSTRUCOES_FINAIS.md**](INSTRUCOES_FINAIS.md)

### Comandos Essenciais

```bash
cd ~
git clone https://github.com/maikonthiago/taskflowai.git TaskFlowAI
cd TaskFlowAI
mkvirtualenv --python=/usr/bin/python3.10 taskflowai
workon taskflowai
pip install -r requirements.txt
python create_admin.py
```

Depois configure WSGI, Static Files e clique em **Reload**.

---

## 🔐 Credenciais Padrão

### Admin
```
Usuário: thiagolobo
Senha: #Wolf@1902
Email: thiago@taskflowai.com
```

⚠️ **IMPORTANTE:** Altere a senha após o primeiro login!

---

## 📁 Estrutura do Projeto

```
TaskFlowAI/
├── app.py                 # Aplicação Flask principal
├── models.py              # Models do banco de dados
├── config.py              # Configurações
├── ai_service.py          # Serviço de IA (OpenAI)
├── stripe_payment.py      # Integração Stripe
├── requirements.txt       # Dependências Python
├── templates/             # Templates HTML
│   ├── base.html
│   ├── landing.html       # Landing page
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html     # Dashboard principal
│   ├── kanban.html        # Board Kanban
│   ├── pricing.html       # Página de preços
│   └── ...
├── static/                # Arquivos estáticos
│   ├── css/
│   ├── js/
│   ├── images/
│   └── avatars/
└── docs/
    ├── INSTRUCOES_FINAIS.md   # 📘 Guia completo
    ├── DEPLOY.md              # 🚀 Guia de deploy
    └── SETUP_PYTHONANYWHERE.sh # ⚡ Script de setup
```

---

## 🎨 Screenshots

<details>
<summary>📸 Ver Screenshots</summary>

### Landing Page
Uma landing page moderna, persuasiva e 100% responsiva.

### Dashboard
Painel completo com estatísticas, tarefas recentes e ações rápidas.

### Kanban Board
Visualização Kanban drag-and-drop para gestão ágil.

### Pricing
Página de preços com 3 planos e integração Stripe.

</details>

---

## 🌐 URLs Importantes

Após o deploy:

- **Homepage:** https://lobtechsolutions.pythonanywhere.com/
- **Login:** https://lobtechsolutions.pythonanywhere.com/login
- **Dashboard:** https://lobtechsolutions.pythonanywhere.com/dashboard
- **Pricing:** https://lobtechsolutions.pythonanywhere.com/pricing
- **API Docs:** https://lobtechsolutions.pythonanywhere.com/api/docs

---

## 📊 Funcionalidades Implementadas

<details>
<summary>📋 Ver Lista Completa</summary>

### Core Features
- [x] Sistema de autenticação (Login/Registro/Recuperação)
- [x] Dashboard com estatísticas em tempo real
- [x] Gestão de Workspaces
- [x] Gestão de Projetos
- [x] Sistema completo de Tarefas
- [x] Subtarefas ilimitadas
- [x] Visualização Lista
- [x] Visualização Kanban
- [x] Visualização Calendário
- [x] Sistema de Tags
- [x] Prioridades (Low, Medium, High, Urgent)
- [x] Status tracking
- [x] Comentários
- [x] Anexos de arquivos
- [x] Checklists dentro de tarefas
- [x] Time tracking

### Colaboração
- [x] Chat interno em tempo real (SocketIO)
- [x] Notificações instantâneas
- [x] Sistema de menções (@user)
- [x] Documentos colaborativos
- [x] Permissões granulares (Owner, Admin, Member, Viewer)
- [x] Convites para workspace
- [x] Activity log

### Inteligência Artificial
- [x] Geração automática de tarefas
- [x] Estruturação de projetos
- [x] Resumo de textos e reuniões
- [x] Análise de dados CSV
- [x] Sugestão de automações
- [x] Assistente virtual Q&A
- [x] Sugestão de deadlines
- [x] Extração de action items

### Módulo Financeiro
- [x] Plano Free (grátis para sempre)
- [x] Plano Pro (R$ 29,90/mês)
- [x] Plano Business (R$ 79,90/mês)
- [x] Integração completa com Stripe
- [x] Trial de 14 dias grátis
- [x] Checkout seguro
- [x] Portal do cliente
- [x] Upgrade/Downgrade automático
- [x] Webhooks do Stripe
- [x] Gestão de assinaturas

### UI/UX
- [x] Design moderno e clean
- [x] 100% responsivo (Mobile First)
- [x] Paleta de cores profissional
- [x] Animações suaves
- [x] Loading states
- [x] Error handling
- [x] Toast notifications
- [x] Tooltips informativos

</details>

---

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
# Flask
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta
JWT_SECRET_KEY=sua-jwt-chave

# Database
DATABASE_URL=mysql+pymysql://user:pass@host/dbname

# Stripe
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OpenAI (opcional)
OPENAI_API_KEY=sk-...

# Email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=email@gmail.com
MAIL_PASSWORD=senha-app
```

---

## 📖 Documentação

- 📘 [**INSTRUCOES_FINAIS.md**](INSTRUCOES_FINAIS.md) - Guia completo e detalhado
- 🚀 [**DEPLOY.md**](DEPLOY.md) - Instruções de deploy no PythonAnywhere
- 📄 [**RESUMO_COMPLETO.txt**](RESUMO_COMPLETO.txt) - Visão geral do projeto

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Add: MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

---

## 📝 Roadmap

- [ ] Aplicativo Mobile (React Native)
- [ ] Integrações (Slack, Discord, Telegram)
- [ ] Relatórios avançados
- [ ] Gantt Chart
- [ ] Whiteboard colaborativo
- [ ] Gravação de áudio para tarefas
- [ ] OCR para digitalização de documentos
- [ ] Dark mode
- [ ] Múltiplos idiomas

---

## 💡 Suporte

Encontrou um bug? Tem uma sugestão?

- 📧 Email: suporte@taskflowai.com
- 💬 Discord: [TaskFlowAI Community](#)
- 🐛 Issues: [GitHub Issues](https://github.com/maikonthiago/taskflowai/issues)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.

---

## 👨‍💻 Autor

**TaskFlowAI Team**

Desenvolvido com ❤️ para revolucionar a gestão de projetos.

---

<div align="center">

### ⭐ Se este projeto te ajudou, deixe uma estrela!

[![GitHub stars](https://img.shields.io/github/stars/maikonthiago/taskflowai?style=social)](https://github.com/maikonthiago/taskflowai/stargazers)

**[⬆ Voltar ao topo](#-taskflowai)**

</div>
