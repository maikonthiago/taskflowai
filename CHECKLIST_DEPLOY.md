# ✅ CHECKLIST DE DEPLOY - TaskFlowAI

Use este checklist para garantir que todos os passos foram concluídos corretamente.

## 📋 Pré-Deploy (Desenvolvimento Local)

- [x] Código completo no GitHub
- [x] README.md atualizado
- [x] Documentação completa (INSTRUCOES_FINAIS.md, DEPLOY.md)
- [x] Scripts de deploy criados
- [x] .env.example configurado
- [x] .gitignore configurado
- [x] Dependências listadas em requirements.txt
- [x] Usuário admin padrão criado

## 🚀 Deploy no PythonAnywhere

### Fase 1: Preparação
- [ ] Conta no PythonAnywhere criada
- [ ] Console Bash aberto
- [ ] Git instalado (já vem instalado)

### Fase 2: Clonar e Instalar
- [ ] Repositório clonado: `git clone https://github.com/maikonthiago/taskflowai.git`
- [ ] Ambiente virtual criado: `mkvirtualenv --python=/usr/bin/python3.10 taskflowai`
- [ ] Ambiente ativado: `workon taskflowai`
- [ ] Dependências instaladas: `pip install -r requirements.txt`

### Fase 3: Banco de Dados
- [ ] Banco MySQL criado no PythonAnywhere (Databases tab)
- [ ] Nome do banco: `lobtechsolutions$lobtechsolutionstaskflowai`
- [ ] Senha do MySQL anotada
- [ ] Banco inicializado: `python -c "from app import app, db; ..."`
- [ ] Usuário admin criado: `python create_admin.py`
- [ ] Login testado: thiagolobo / #Wolf@1902

### Fase 4: Configuração
- [ ] Arquivo `.env` criado
- [ ] `DATABASE_URL` configurado com senha real do MySQL
- [ ] `SECRET_KEY` gerada (chave forte)
- [ ] `JWT_SECRET_KEY` gerada (chave forte)

### Fase 5: Web App
- [ ] Web app criado no PythonAnywhere (Web tab)
- [ ] Python 3.10 selecionado
- [ ] Arquivo WSGI configurado (copiar de DEPLOY.md)
- [ ] Virtualenv path configurado: `/home/lobtechsolutions/.virtualenvs/taskflowai`
- [ ] Static files configurado: `/static/` → `/home/lobtechsolutions/TaskFlowAI/static`
- [ ] Botão "Reload" clicado

### Fase 6: Stripe (Opcional mas Recomendado)
- [ ] Conta Stripe criada: https://stripe.com
- [ ] Modo de teste ativado
- [ ] Chaves obtidas (Dashboard → API keys)
- [ ] `STRIPE_PUBLIC_KEY` no .env
- [ ] `STRIPE_SECRET_KEY` no .env
- [ ] Produtos criados no Stripe Dashboard
- [ ] Preços configurados
- [ ] Webhook configurado (se necessário)

### Fase 7: OpenAI (Opcional)
- [ ] Conta OpenAI criada: https://platform.openai.com
- [ ] API key obtida
- [ ] `OPENAI_API_KEY` no .env
- [ ] Créditos carregados na conta

## 🧪 Testes Pós-Deploy

### Testes Básicos
- [ ] Site carrega: https://lobtechsolutions.pythonanywhere.com/
- [ ] Landing page exibe corretamente
- [ ] Página de login acessível: /login
- [ ] Página de registro acessível: /register
- [ ] CSS e JS carregando (verificar no DevTools)

### Testes de Funcionalidade
- [ ] Registro de novo usuário funciona
- [ ] Login com admin funciona (thiagolobo / #Wolf@1902)
- [ ] Dashboard carrega após login
- [ ] Logout funciona
- [ ] Criar workspace funciona
- [ ] Criar projeto funciona
- [ ] Criar tarefa funciona
- [ ] Visualização Kanban funciona
- [ ] Chat carrega (mesmo sem mensagens)

### Testes de Responsividade
- [ ] Mobile (< 768px) - testado
- [ ] Tablet (768px - 1024px) - testado
- [ ] Desktop (> 1024px) - testado
- [ ] Menu mobile funciona
- [ ] Sidebar recolhe no mobile

### Testes de API
- [ ] `GET /api/workspaces` - retorna 200
- [ ] `GET /api/projects` - retorna 200
- [ ] `GET /api/tasks` - retorna 200
- [ ] `POST /api/tasks` - cria tarefa
- [ ] Autenticação JWT funciona

### Testes de Stripe (se configurado)
- [ ] Página de pricing carrega: /pricing
- [ ] Toggle anual/mensal funciona
- [ ] Botão de checkout funciona
- [ ] Redirecionamento para Stripe funciona
- [ ] Checkout de teste completa com sucesso

### Testes de IA (se configurado)
- [ ] Endpoint `/api/ai/generate-tasks` responde
- [ ] IA gera tarefas a partir de descrição
- [ ] Erro tratado se API key inválida

## 🐛 Troubleshooting

### Problema: Site não carrega (502 Bad Gateway)
- [ ] Verificar logs: `/var/log/lobtechsolutions.pythonanywhere.com.error.log`
- [ ] Verificar se virtualenv está correto
- [ ] Verificar se arquivo WSGI está correto
- [ ] Tentar reload novamente

### Problema: Erro de banco de dados
- [ ] Verificar se banco foi criado
- [ ] Verificar credenciais no .env
- [ ] Verificar se DATABASE_URL está correto
- [ ] Testar conexão manual no console MySQL

### Problema: Static files não carregam
- [ ] Verificar configuração de Static Files no Web tab
- [ ] Verificar permissões da pasta /static
- [ ] Verificar se arquivos existem
- [ ] Fazer reload

### Problema: Imports falhando
- [ ] Verificar se todas as dependências foram instaladas
- [ ] Verificar se virtualenv está ativo
- [ ] Reinstalar: `pip install -r requirements.txt`

## 📊 Monitoramento

### Logs
- [ ] Error log verificado: sem erros críticos
- [ ] Server log verificado: requisições passando
- [ ] Access log: tráfego normal

### Performance
- [ ] Tempo de resposta < 2s
- [ ] Páginas carregando rápido
- [ ] Sem memory leaks
- [ ] CPU usage normal

### Segurança
- [ ] HTTPS habilitado (PythonAnywhere faz automaticamente)
- [ ] Senhas hashadas (bcrypt/werkzeug)
- [ ] JWT tokens expirando corretamente
- [ ] .env não está no Git (verificar .gitignore)
- [ ] SECRET_KEY não é a padrão

## 🎉 Finalização

### Documentação
- [ ] README.md lido e compreendido
- [ ] INSTRUCOES_FINAIS.md consultado
- [ ] DEPLOY.md seguido
- [ ] URLs documentadas

### Backup
- [ ] Backup do banco de dados feito
- [ ] Backup dos arquivos feito
- [ ] Credenciais salvas em local seguro

### Comunicação
- [ ] Time notificado sobre deploy
- [ ] Usuários informados sobre acesso
- [ ] Documentação compartilhada

## 📞 Próximos Passos

- [ ] Configurar domínio personalizado (opcional)
- [ ] Configurar email SMTP para notificações
- [ ] Adicionar mais usuários admin
- [ ] Configurar backups automáticos
- [ ] Monitorar uso de recursos
- [ ] Coletar feedback dos usuários
- [ ] Planejar próximas features

## ✅ Status Final

Data de Deploy: ____/____/______
Deploy realizado por: ___________________
Status: [ ] Sucesso  [ ] Parcial  [ ] Falhou
Observações:
_________________________________________________
_________________________________________________
_________________________________________________

---

**🎉 Parabéns! TaskFlowAI está no ar!**

Site: https://lobtechsolutions.pythonanywhere.com/
Admin: thiagolobo / #Wolf@1902
