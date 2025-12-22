# TaskFlowAI 🚀

**Seu fluxo de trabalho, inteligente e simples.**

Sistema completo de gerenciamento de projetos e tarefas com IA integrada, superior ao ClickUp.

## 🎯 Funcionalidades

- ✅ Gerenciamento completo de tarefas e projetos
- 🎨 Visualizações: Lista, Kanban, Calendário, Timeline
- 👥 Sistema de equipes e permissões
- 💬 Chat interno em tempo real
- 📝 Documentos colaborativos
- 🎯 Whiteboard para brainstorming
- 🤖 IA integrada para automação e insights
- 💳 Módulo financeiro com Stripe
- 📱 100% Responsivo (Mobile First)

## 🛠️ Tecnologias

**Backend:**
- Python 3.11+
- Flask
- SQLAlchemy
- MySQL/PostgreSQL
- JWT Authentication
- SocketIO para real-time

**Frontend:**
- HTML5
- Bootstrap 5.3
- JavaScript (Vanilla)
- CSS3 customizado

**IA:**
- OpenAI API
- Automação inteligente

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/maikonthiago/taskflowai.git
cd taskflowai

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações

# Inicialize o banco de dados
flask db upgrade

# Crie usuário admin
python create_admin.py

# Execute o servidor
python app.py
```

## 🚀 Deploy no PythonAnywhere

```bash
# Siga as instruções em DEPLOY.md
```

## 👤 Usuário Admin Padrão

- **Usuário:** thiagolobo
- **Senha:** #Wolf@1902

⚠️ **IMPORTANTE:** Altere a senha após o primeiro login!

## 📄 Licença

MIT License

## 👨‍💻 Autor

Desenvolvido com ❤️ para revolucionar a gestão de projetos.
