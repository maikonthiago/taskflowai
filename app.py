import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_mail import Mail, Message
from threading import Thread
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
from functools import wraps
from sqlalchemy import or_, func
import requests
from abacate_payment import AbacatePayment

from config import config
from models import (
    db,
    User,
    Workspace,
    Space,
    Project,
    TaskList,
    Task,
    Comment,
    Attachment,
    Message,
    Notification,
    WorkspaceInvite,
    SubscriptionPlan,
    SystemSetting,
    Goal,
    System,
    MicroAction,
    DailyLog,
    CompletedAction
)
from ai_service import AIService

from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import Babel, _, refresh

# ... imports ...
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory, session

app = Flask(__name__)
# Load config first
app.config.from_object(config[os.environ.get('FLASK_ENV', 'development')])

# I18N Config
app.config['BABEL_DEFAULT_LOCALE'] = 'pt'
app.config['BABEL_SUPPORTED_LOCALES'] = ['pt', 'en', 'es']

def get_locale():
    # 1. Check session
    if 'lang' in session:
        return session['lang']
    # 2. Check user preference (if logged in) - skipped for now to keep simple
    # 3. Check browser basic
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

babel = Babel(app, locale_selector=get_locale)

@app.route('/sw.js')
def service_worker():
    response = send_from_directory('static', 'sw.js')
    response.headers['Cache-Control'] = 'no-cache'
    return response

# Security Init
csrf = CSRFProtect(app)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["2000 per day", "500 per hour"],
    storage_uri="memory://"
)

@app.route('/set_language/<lang_code>')
def set_language(lang_code):
    if lang_code in app.config['BABEL_SUPPORTED_LOCALES']:
        session['lang'] = lang_code
        refresh() # Refresh babel context
    return redirect(request.referrer or url_for('landing'))

# Configurar APPLICATION_ROOT de forma dinâmica
app_root = os.environ.get('FLASK_APP_ROOT', '/')
app.config['APPLICATION_ROOT'] = app_root
app.config['SESSION_COOKIE_PATH'] = app_root
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Evita expiração prematura do token

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/avatars', exist_ok=True)

# Inicializar extensões
db.init_app(app)
mail = Mail(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Inicializar serviço de IA
ai_service = AIService(app.config.get('OPENAI_API_KEY'))

DEFAULT_PLAN_SEEDS = [
    {
        'name': 'Free',
        'slug': 'free',
        'description': 'Para começar sem custos e testar o TaskFlowAI.',
        'badge_text': 'Grátis',
        'highlight': False,
        'is_default': True,
        'order': 0,
        'price_monthly': 0.0,
        'price_yearly': 0.0,
        'features': [
            '1 workspace ativo',
            '3 projetos simultâneos',
            'Até 100 tarefas',
            '3 membros colaboradores',
            '100 MB de armazenamento',
            '10 requisições de IA/mês'
        ]
    },
    {
        'name': 'Pro',
        'slug': 'pro',
        'description': 'Para equipes que precisam de recursos avançados.',
        'badge_text': 'Mais Popular',
        'highlight': True,
        'is_default': False,
        'order': 1,
        'price_monthly': 29.9,
        'price_yearly': 287.0,
        'features': [
            '5 workspaces',
            'Projetos ilimitados',
            'Tarefas ilimitadas',
            '20 membros colaboradores',
            '10 GB de armazenamento',
            '500 requisições de IA/mês',
            'Automações avançadas',
            'Suporte prioritário'
        ]
    },
    {
        'name': 'Business',
        'slug': 'business',
        'description': 'Perfeito para empresas em crescimento.',
        'badge_text': 'Equipes',
        'highlight': False,
        'is_default': False,
        'order': 2,
        'price_monthly': 79.9,
        'price_yearly': 767.0,
        'features': [
            'Workspaces ilimitados',
            'Projetos ilimitados',
            'Membros ilimitados',
            '100 GB de armazenamento',
            'IA ilimitada',
            'Automações ilimitadas',
            'Suporte 24/7',
            'Onboarding dedicado'
        ]
    }
]

DEFAULT_SYSTEM_SETTINGS = [
    {
        'key': 'OPENAI_API_KEY',
        'category': 'integrations',
        'description': 'Chave utilizada pelos recursos de IA.',
        'is_secret': True
    },
    {
        'key': 'ABACATE_API_KEY',
        'category': 'payments',
        'description': 'Chave API da AbacatePay.',
        'is_secret': True
    }
]

RUNTIME_SETTING_MAP = {
    'OPENAI_API_KEY': 'OPENAI_API_KEY',
    'ABACATE_API_KEY': 'ABACATE_API_KEY'
}


def normalize_features(raw_features):
    if isinstance(raw_features, list):
        return [item.strip() for item in raw_features if item and item.strip()]
    if isinstance(raw_features, str):
        return [line.strip() for line in raw_features.splitlines() if line.strip()]
    return []


def parse_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def ensure_subscription_plans():
    created = False
    for plan_seed in DEFAULT_PLAN_SEEDS:
        if SubscriptionPlan.query.filter_by(slug=plan_seed['slug']).first():
            continue
        data = dict(plan_seed)
        config_plans = app.config.get('PLANS', {})
        config_plan = config_plans.get(plan_seed['slug'])
        if config_plan:
            data.setdefault('price_monthly', config_plan.get('price', data.get('price_monthly', 0)))
            if config_plan.get('stripe_price_id'):
                data['stripe_price_monthly_id'] = config_plan['stripe_price_id']
        if data.get('price_yearly') is None:
            monthly = data.get('price_monthly') or 0
            data['price_yearly'] = round(monthly * 12 * 0.8, 2) if monthly else 0
        data['features'] = normalize_features(data.get('features'))
        plan = SubscriptionPlan(**data)
        db.session.add(plan)
        created = True
    if created:
        db.session.commit()


def ensure_system_settings():
    created = False
    for definition in DEFAULT_SYSTEM_SETTINGS:
        setting = SystemSetting.query.filter_by(key=definition['key']).first()
        if setting:
            continue
        value = app.config.get(definition['key'])
        setting = SystemSetting(value=value, **definition)
        db.session.add(setting)
        created = True
    if created:
        db.session.commit()


def get_setting_value(key, fallback=None):
    setting = SystemSetting.query.filter_by(key=key).first()
    if setting and setting.value:
        return setting.value
    return fallback


def apply_runtime_setting(key, value):
    app.config[key] = value
    if key == 'OPENAI_API_KEY':
        ai_service.set_api_key(value)


def refresh_integrations_cache():
    for setting_key, config_key in RUNTIME_SETTING_MAP.items():
        value = get_setting_value(setting_key, app.config.get(config_key))
        if value is not None:
            apply_runtime_setting(config_key, value)


def ensure_default_data():
    ensure_subscription_plans()
    ensure_system_settings()
    refresh_integrations_cache()


def get_active_plans(include_inactive=False):
    query = SubscriptionPlan.query
    if not include_inactive:
        query = query.filter_by(is_active=True)
    return query.order_by(SubscriptionPlan.order.asc(), SubscriptionPlan.price_monthly.asc()).all()


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        if not current_user.is_admin:
            if request.path.startswith('/api/') or request.is_json:
                return jsonify({'error': 'Acesso restrito aos administradores'}), 403
            flash('Acesso restrito aos administradores.', 'danger')
            return redirect('/taskflowai/dashboard')
        return view_func(*args, **kwargs)

    return wrapper

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def maintain_super_admin_status():
    if current_user.is_authenticated and current_user.username == 'thiagolobo':
        if current_user.subscription_plan != 'business':
            current_user.subscription_plan = 'business'
            db.session.commit()

# ==================== EMAIL HELPER ====================
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Erro ao enviar email: {e}")

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config.get('MAIL_USERNAME')
    )
    Thread(target=send_async_email, args=(app, msg)).start()


# ==================== INICIALIZAÇÃO ====================

with app.app_context():
    try:
        db.create_all()
        ensure_default_data()
    except Exception as e:
        print(f"Erro na inicialização: {e}")

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ==================== ROTAS PÚBLICAS ====================

@app.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_console'))
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user and user.check_password(password):
            login_user(user, remember=data.get('remember', False))
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.is_admin:
                    next_page = url_for('admin_console')
                else:
                    next_page = url_for('dashboard')
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login realizado com sucesso',
                    'redirect': next_page
                })
            return redirect(next_page)
        
        if request.is_json:
            return jsonify({'success': False, 'message': 'Usuário ou senha inválidos'}), 401
        flash('Usuário ou senha inválidos', 'danger')
    
    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Gerar token de reset (válido por 1 hora)
            expires = timedelta(hours=1)
            reset_token = create_access_token(identity=user.id, expires_delta=expires, additional_claims={'type': 'reset'})
            
            # Envio de Email Real
            reset_link = url_for('reset_password_token', token=reset_token, _external=True)
            
            html_body = f"""
            <h3>Recuperação de Senha - RitualOS</h3>
            <p>Olá {user.full_name},</p>
            <p>Você solicitou a redefinição de sua senha. Clique no link abaixo para prosseguir:</p>
            <p><a href="{reset_link}">{reset_link}</a></p>
            <p>Se você não solicitou isso, ignore este email.</p>
            """
            
            send_email(user.email, "Recuperação de Senha - RitualOS", html_body)

            
            flash('Se o email existir, enviamos um link para redefinir sua senha. (Cheque o console do servidor para o link simulado)', 'info')
        else:
             # Mesma mensagem para não vazar usuários
             flash('Se o email existir, enviamos um link para redefinir sua senha.', 'info')
             
        return redirect(url_for('login'))
        
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password_token(token):
    try:
        # Verificar token
        decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded_token['sub']
        claim_type = decoded_token.get('type')
        
        if claim_type != 'reset':
            flash('Token inválido ou expirado.', 'danger')
            return redirect(url_for('login'))
            
        if request.method == 'POST':
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                flash('As senhas não coincidem.', 'danger')
                return render_template('reset_password.html', token=token)
                
            user = User.query.get(user_id)
            if user:
                user.set_password(password)
                db.session.commit()
                flash('Sua senha foi atualizada com sucesso! Faça login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Usuário não encontrado.', 'danger')
                return redirect(url_for('login'))
                
        return render_template('reset_password.html', token=token)
        
    except Exception as e:
        flash('O link de redefinição é inválido ou expirou.', 'danger')
        return redirect(url_for('forgot_password'))

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def register():
    """Página de registro"""
    invite_token = request.args.get('invite_token') or request.form.get('invite_token')

    if current_user.is_authenticated:
        return redirect('/taskflowai/dashboard')
    
    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        
        # Validar dados
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        
        if User.query.filter_by(username=username).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Nome de usuário já existe'}), 400
            flash('Nome de usuário já existe', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'success': False, 'message': 'Email já cadastrado'}), 400
            flash('Email já cadastrado', 'danger')
            return render_template('register.html')
        
        # Criar usuário
        user = User(
            username=username,
            email=email,
            full_name=full_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Criar workspace padrão
        workspace = Workspace(
            name=f"Workspace de {full_name or username}",
            slug=f"workspace-{user.id}",
            owner_id=user.id
        )
        db.session.add(workspace)
        workspace.members.append(user)
        db.session.commit()

        if invite_token:
            invite = WorkspaceInvite.query.filter_by(token=invite_token, status='pending').first()
            if invite:
                target_workspace = invite.workspace
                if user not in target_workspace.members:
                    target_workspace.members.append(user)
                invite.status = 'accepted'
                invite.accepted_at = datetime.utcnow()
                db.session.commit()
                invite.accepted_at = datetime.utcnow()
                db.session.commit()
                flash(f'Convite aceito! Você agora participa do workspace {target_workspace.name}', 'success')
        
        # Admin Notification
        try:
            admin_email = 'thiagolobopersonaltrainer@gmail.com'
            send_email(admin_email, f"Novo Usuário: {full_name}", f"Usuário {username} ({email}) acabou de se registrar.")
            
            # Welcome Email
            send_email(email, "Bem-vindo ao RitualOS", f"Olá {full_name},<br>Bem-vindo ao RitualOS! Sua jornada de consistência começa agora.")
        except:
             pass

        login_user(user)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Conta criada com sucesso',
                'redirect': '/taskflowai/dashboard'
            })
        
        flash('Conta criada com sucesso!', 'success')
        return redirect('/taskflowai/dashboard')
    
    return render_template('register.html', invite_token=invite_token)

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect('/taskflowai/')

@app.route('/pricing')
def pricing():
    """Página de preços"""
    plans = get_active_plans()
    return render_template('pricing.html', plans=plans)

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal - RitualOS"""
    return render_template('ritual_dashboard.html', user=current_user)

# ==================== WORKSPACES ====================

@app.route('/workspace/<int:workspace_id>')
@login_required
def workspace_detail(workspace_id):
    """Detalhes do workspace"""
    workspace = Workspace.query.get_or_404(workspace_id)
    
    # Verificar permissão
    if current_user not in workspace.members and workspace.owner_id != current_user.id:
        flash('Você não tem permissão para acessar este workspace', 'danger')
        return redirect('/taskflowai/dashboard')
    
    projects = Project.query.filter_by(workspace_id=workspace_id, is_active=True).all()
    spaces = Space.query.filter_by(workspace_id=workspace_id, is_active=True).all()
    
    return render_template('workspace.html',
                         workspace=workspace,
                         projects=projects,
                         spaces=spaces)

# ==================== PROJECTS ====================

@app.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    """Detalhes do projeto"""
    project = Project.query.get_or_404(project_id)
    
    # Verificar permissão
    workspace = project.workspace
    if current_user not in workspace.members and workspace.owner_id != current_user.id:
        flash('Você não tem permissão para acessar este projeto', 'danger')
        return redirect('/taskflowai/dashboard')
    
    lists = TaskList.query.filter_by(project_id=project_id, is_active=True)\
        .order_by(TaskList.position).all()
    
    tasks = Task.query.filter_by(project_id=project_id, is_active=True)\
        .order_by(Task.position).all()
    
    return render_template('project.html',
                         project=project,
                         lists=lists,
                         tasks=tasks,
                         view=request.args.get('view', 'list'))

@app.route('/project/<int:project_id>/kanban')
@login_required
def project_kanban(project_id):
    """Visualização Kanban"""
    project = Project.query.get_or_404(project_id)
    return render_template('kanban.html', project=project)

@app.route('/project/<int:project_id>/calendar')
@login_required
def project_calendar(project_id):
    """Visualização Calendário"""
    project = Project.query.get_or_404(project_id)
    return render_template('calendar.html', project=project)

# ==================== TASKS ====================

@app.route('/tasks')
@login_required
def tasks_view():
    """Lista tarefas criadas ou atribuídas ao usuário atual"""
    tasks = Task.query.filter(
        or_(Task.creator_id == current_user.id,
            Task.assignees.any(User.id == current_user.id))
    ).filter_by(is_active=True)
    tasks = tasks.order_by(Task.due_date.asc(), Task.created_at.desc()).all()
    return render_template('tasks.html', tasks=tasks)

@app.route('/task/<int:task_id>')
@login_required
def task_detail(task_id):
    """Detalhes da tarefa"""
    task = Task.query.get_or_404(task_id)
    
    # Verificar permissão
    workspace = task.project.workspace
    if current_user not in workspace.members and workspace.owner_id != current_user.id:
        flash('Você não tem permissão para acessar esta tarefa', 'danger')
        return redirect('/taskflowai/dashboard')
    
    comments = Comment.query.filter_by(task_id=task_id)\
        .order_by(Comment.created_at.desc()).all()
    
    return render_template('task.html', task=task, comments=comments)

# ==================== CHAT ====================

@app.route('/chat')
@login_required
def chat():
    """Chat interno"""
    workspaces = current_user.workspaces
    return render_template('chat.html', workspaces=workspaces)

# ==================== DOCUMENTS ====================

@app.route('/documents')
@login_required
def documents():
    """Documentos colaborativos"""
    return render_template('documents.html')

# ==================== SETTINGS ====================

@app.route('/settings')
@login_required
def settings():
    """Configurações do usuário"""
    return render_template('settings.html')

@app.route('/settings/subscription')
@login_required
def subscription_settings():
    """Configurações de assinatura"""
    plans = get_active_plans()
    return render_template('subscription.html', user=current_user, plans=plans)


@app.route('/admin/console')
@admin_required
def admin_console():
    """Painel administrativo centralizado"""
    ensure_default_data()
    now = datetime.utcnow()
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'new_users': User.query.filter(User.created_at >= (now - timedelta(days=30))).count(),
        'admin_users': User.query.filter_by(is_admin=True).count(),
        'paid_users': User.query.filter(User.subscription_plan != 'free').count(),
        'active_goals': Goal.query.filter_by(status='active').count(),
        'total_systems': System.query.count(),
        'total_completions': CompletedAction.query.count()
    }

    plans = get_active_plans(include_inactive=True)
    plan_lookup = {plan.slug: plan.name for plan in plans}
    plan_counts = db.session.query(User.subscription_plan, func.count(User.id)).group_by(User.subscription_plan).all()
    plan_usage = [
        {
            'label': plan_lookup.get(slug, slug.capitalize() if slug else 'Não definido'),
            'value': count
        }
        for slug, count in plan_counts
    ]

    settings_records = SystemSetting.query.order_by(SystemSetting.category.asc(), SystemSetting.key.asc()).all()
    settings_payload = []
    for record in settings_records:
        info = record.to_dict(include_value=not record.is_secret)
        if record.is_secret:
            info['value'] = ''
        settings_payload.append(info)

    admin_state = {
        'stats': stats,
        'planUsage': plan_usage,
        'plans': [plan.to_dict() for plan in plans],
        'settings': settings_payload
    }

    return render_template('admin_dashboard.html', stats=stats, plan_usage=plan_usage, admin_state=admin_state)

# ==================== ABACATE PAY & LIMITS ====================
@app.route('/api/create-checkout', methods=['POST'])
@login_required
def create_checkout():
    """Criar sessão de pagamento na AbacatePay"""
    data = request.json
    plan_slug = data.get('plan')
    billing_period = data.get('billing', 'monthly') # monthly ou yearly
    
    plan = SubscriptionPlan.query.filter_by(slug=plan_slug).first_or_404()
    
    amount = plan.price_monthly
    if billing_period == 'yearly' and plan.price_yearly:
        amount = plan.price_yearly
    
    amount_cents = int(amount * 100)
    
    # 1. Garantir Cliente
    # Por simplicidade, vamos sempre tentar criar/atualizar ou usar email
    # Idealmente salvaríamos o abacate_customer_id no User
    customer = AbacatePayment.create_customer(current_user.full_name or current_user.username, current_user.email)
    if not customer or 'data' not in customer:
         return jsonify({'error': 'Erro ao criar cliente no gateway'}), 500
    
    customer_id = customer['data']['id']
    
    # 2. Criar Cobrança
    return_url = url_for('dashboard', _external=True)
    completion_url = url_for('dashboard', _external=True)
    
    description = f"Assinatura {plan.name} ({billing_period})"
    
    billing = AbacatePayment.create_billing(
        customer_id=customer_id,
        amount_cents=amount_cents,
        description=description,
        return_url=return_url,
        completion_url=completion_url
    )
    
    if not billing or 'data' not in billing:
         return jsonify({'error': 'Erro ao gerar pagamento'}), 500
         
    payment_url = billing['data']['url']
    
    return jsonify({'url': payment_url})


@app.route('/abacate_webhook', methods=['POST'])
def abacate_webhook():
    data = request.json
    
    # Validar webhook (simplificado, idealmente verificar assinatura ou token secreto)
    # A estrutura do payload da AbacatePay varia, vamos assumir padrão evento.
    event_type = data.get('event')
    
    if event_type == 'billing.paid':
        billing_data = data.get('data', {}).get('billing', {})
        customer_data = data.get('data', {}).get('customer', {})
        email = customer_data.get('email')
        
        # Encontrar usuário e liberar acesso
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                # Lógica simples: se pagou qualquer valor > 20, vira Pro. Se > 70, Business.
                # Ou melhorar passando metadata no billing.
                amount = billing_data.get('amount', 0)
                
                new_plan = 'free'
                if amount > 7000: # 70.00
                    new_plan = 'business'
                elif amount > 2000: # 20.00
                    new_plan = 'pro'
                
                user.subscription_plan = new_plan
                user.subscription_status = 'active'
                db.session.commit()
                
                # Notificar Sistema
                notif = Notification(
                    title='Pagamento Confirmado! 🚀',
                    content=f'Sua assinatura {new_plan.capitalize()} está ativa.',
                    type='system',
                    user_id=user.id
                )
                db.session.add(notif)
                db.session.commit()
                
                # Email User
                send_email(email, "Pagamento Confirmado - RitualOS", f"Sua assinatura {new_plan} foi confirmada! Aproveite.")
                
                # Email Admin
                try:
                    send_email('thiagolobopersonaltrainer@gmail.com', "Venda Realizada!", f"Usuário {email} assinou o plano {new_plan}. Valor: {amount/100}")
                except:
                    pass
                
    return jsonify({'status': 'ok'}), 200

# Usage Limits Logic
PLAN_LIMITS = {
    'free': {'projects': 3, 'members': 3, 'ai_requests': 10},
    'pro': {'projects': 9999, 'members': 20, 'ai_requests': 500},
    'business': {'projects': 9999, 'members': 9999, 'ai_requests': 9999}
}

def check_limit(limit_type):
    """Check if current_user has reached the limit for a feature"""
    plan = current_user.subscription_plan or 'free'
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS['free'])
    limit_val = limits.get(limit_type, 0)
    
    if limit_val >= 9999: # Unlimited
        return True, 0
        
    current_val = 0
    if limit_type == 'projects':
        # Count owned projects
        current_val = Project.query.filter(
            Project.workspace_id.in_([w.id for w in current_user.owned_workspaces])
        ).count()
    elif limit_type == 'members':
        # Max members in any workspace owned by user
        max_members = 0
        for w in current_user.owned_workspaces:
            if len(w.members) > max_members:
                max_members = len(w.members)
        current_val = max_members
    elif limit_type == 'ai_requests':
        # TODO: Implement AI usage counter in User model or Redis
        # For now, simplistic approximation or placeholder
        current_val = 0 
        
    if current_val >= limit_val:
        return False, limit_val
    return True, limit_val


@app.route('/api/check-auth', methods=['GET'])
def api_check_auth():
    """Verifica o status de autenticação do usuário"""
    if current_user.is_authenticated:
        return jsonify({'authenticated': True}), 200
    return jsonify({'authenticated': False}), 401

# API - Workspaces
@app.route('/api/workspaces', methods=['GET', 'POST'])
@login_required
def api_workspaces():
    if request.method == 'GET':
        workspaces = current_user.workspaces + current_user.owned_workspaces
        return jsonify([w.to_dict() for w in workspaces])
    
    elif request.method == 'POST':
        data = request.get_json()
        workspace = Workspace(
            name=data['name'],
            slug=data.get('slug', data['name'].lower().replace(' ', '-')),
            description=data.get('description'),
            owner_id=current_user.id
        )
        db.session.add(workspace)
        workspace.members.append(current_user)
        db.session.commit()
        return jsonify(workspace.to_dict()), 201


@app.route('/api/workspaces/<int:workspace_id>/invite', methods=['POST'])
@login_required
def api_workspace_invite(workspace_id):
    # Check Member Limits
    is_allowed, limit = check_limit('members')
    if not is_allowed:
        return jsonify({
            'error': f'Limite de membros atingido ({limit}). Faça upgrade para convidar mais pessoas!',
            'upgrade_required': True
        }), 403

    workspace = Workspace.query.get_or_404(workspace_id)
    if current_user not in workspace.members and workspace.owner_id != current_user.id:
        return jsonify({'error': 'Você não tem permissão para convidar membros neste workspace'}), 403
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email é obrigatório'}), 400
    user = User.query.filter_by(email=email).first()
    if user:
        if user not in workspace.members:
            workspace.members.append(user)
            db.session.commit()
        return jsonify({'success': True, 'message': 'Usuário adicionado ao workspace'}), 200
    invite = WorkspaceInvite.query.filter_by(workspace_id=workspace.id, email=email, status='pending').first()
    if not invite:
        invite = WorkspaceInvite(
            workspace_id=workspace.id,
            email=email,
            invited_by=current_user.id
        )
        db.session.add(invite)
        db.session.commit()
    invite_link = url_for('register', invite_token=invite.token, _external=True)
    return jsonify({'success': True, 'message': 'Convite criado', 'invite_link': invite_link}), 201

# API - Projects
@app.route('/api/projects', methods=['GET', 'POST'])
@login_required
def api_projects():
    if request.method == 'GET':
        workspace_id = request.args.get('workspace_id')
        if workspace_id:
            projects = Project.query.filter_by(workspace_id=workspace_id, is_active=True).all()
        else:
            # Todos os projetos dos workspaces do usuário
            workspace_ids = [w.id for w in current_user.workspaces + current_user.owned_workspaces]
            projects = Project.query.filter(Project.workspace_id.in_(workspace_ids), Project.is_active == True).all()
        
        return jsonify([p.to_dict() for p in projects])
    
    elif request.method == 'POST':
        # Check Project Limits
        is_allowed, limit = check_limit('projects')
        if not is_allowed:
            return jsonify({
                'error': f'Limite de projetos atingido ({limit}). Faça upgrade para criar ilimitados!',
                'upgrade_required': True
            }), 403

        data = request.get_json()
        project = Project(
            name=data['name'],
            description=data.get('description'),
            workspace_id=data['workspace_id'],
            space_id=data.get('space_id'),
            color=data.get('color', '#1E64F0')
        )
        db.session.add(project)
        db.session.commit()
        return jsonify(project.to_dict()), 201

# API - Tasks
@app.route('/api/tasks', methods=['GET', 'POST'])
@login_required
def api_tasks():
    if request.method == 'GET':
        project_id = request.args.get('project_id')
        list_id = request.args.get('list_id')
        status = request.args.get('status')
        
        query = Task.query.filter_by(is_active=True)
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        if list_id:
            query = query.filter_by(list_id=list_id)
        if status:
            query = query.filter_by(status=status)
        
        tasks = query.order_by(Task.position).all()
        return jsonify([t.to_dict() for t in tasks])
    
    elif request.method == 'POST':
        data = request.get_json()
        if 'project_id' not in data:
            return jsonify({'error': 'Projeto é obrigatório'}), 400
        project_id = data['project_id']
        try:
            project_id = int(project_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'Projeto inválido'}), 400
        project = Project.query.get_or_404(project_id)
        workspace = project.workspace
        if current_user not in workspace.members and workspace.owner_id != current_user.id:
            return jsonify({'error': 'Você não tem acesso a este projeto'}), 403
        task = Task(
            title=data['title'],
            description=data.get('description'),
            project_id=project_id,
            list_id=data.get('list_id'),
            creator_id=current_user.id,
            status=data.get('status', 'todo'),
            priority=data.get('priority', 'medium'),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
        )
        db.session.add(task)
        db.session.commit()
        
        # Criar notificação para assignees
        if data.get('assignee_ids'):
            for user_id in data['assignee_ids']:
                user = User.query.get(user_id)
                if user:
                    task.assignees.append(user)
                    notification = Notification(
                        title='Nova tarefa atribuída',
                        content=f'Você foi atribuído à tarefa: {task.title}',
                        type='task_assigned',
                        link=f'/task/{task.id}',
                        user_id=user_id
                    )
                    db.session.add(notification)
        
        db.session.commit()
        return jsonify(task.to_dict()), 201

@app.route('/api/tasks/<int:task_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def api_task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'GET':
        return jsonify(task.to_dict())
    
    elif request.method == 'PUT':
        data = request.get_json()
        
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'done' and not task.completed_at:
                task.completed_at = datetime.utcnow()
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        if 'list_id' in data:
            task.list_id = data['list_id']
        if 'position' in data:
            task.position = data['position']
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(task.to_dict())
    
    elif request.method == 'DELETE':
        task.is_active = False
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tarefa excluída'})

# API - Comments
@app.route('/api/tasks/<int:task_id>/comments', methods=['GET', 'POST'])
@login_required
def api_task_comments(task_id):
    task = Task.query.get_or_404(task_id)
    
    if request.method == 'GET':
        comments = Comment.query.filter_by(task_id=task_id)\
            .order_by(Comment.created_at.desc()).all()
        return jsonify([c.to_dict() for c in comments])
    
    elif request.method == 'POST':
        data = request.get_json()
        comment = Comment(
            content=data['content'],
            task_id=task_id,
            author_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        
        return jsonify(comment.to_dict()), 201

# API - Notifications
@app.route('/api/notifications')
@login_required
def api_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify([n.to_dict() for n in notifications])

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def api_mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    notification.is_read = True
    db.session.commit()
    return jsonify({'success': True})

# API - IA
@app.route('/api/ai/generate-tasks', methods=['POST'])
@login_required
def api_ai_generate_tasks():
    """Gerar tarefas usando IA"""
    # Check AI Usage Limits
    is_allowed, limit = check_limit('ai_requests')
    if not is_allowed:
        return jsonify({
            'error': f'Limite de uso da IA atingido ({limit}). Faça upgrade para mais poder!',
            'upgrade_required': True
        }), 403

    data = request.get_json()
    description = data.get('description')
    project_id = data.get('project_id')
    
    if not description:
        return jsonify({'error': 'Descrição é obrigatória'}), 400
    if not project_id:
        return jsonify({'error': 'Projeto destino é obrigatório'}), 400
    try:
        project_id = int(project_id)
    except (TypeError, ValueError):
        return jsonify({'error': 'Projeto inválido'}), 400
    target_project = Project.query.get_or_404(project_id)
    workspace = target_project.workspace
    if current_user not in workspace.members and workspace.owner_id != current_user.id:
        return jsonify({'error': 'Você não tem acesso a este projeto'}), 403
    
    refresh_integrations_cache()
    try:
        tasks_data = ai_service.generate_tasks_from_description(description)
        
        # Criar tarefas no banco
        created_tasks = []
        for task_data in tasks_data:
            task = Task(
                title=task_data['title'],
                description=task_data.get('description'),
                project_id=target_project.id,
                creator_id=current_user.id,
                priority=task_data.get('priority', 'medium'),
                status='todo'
            )
            db.session.add(task)
            created_tasks.append(task)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'tasks': [t.to_dict() for t in created_tasks]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ADMIN DASHBOARD UI ====================

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Calcular estatísticas reais
    now = datetime.utcnow()
    total_users = User.query.count()
    new_users = User.query.filter(User.created_at >= (now - timedelta(days=30))).count()
    
    # Assinaturas (Exemplo simples, idealmente buscaria do User.subscription_plan)
    active_subs = User.query.filter(User.subscription_plan.in_(['pro', 'business'])).count()
    total_projects = Project.query.count()
    active_workspaces = Workspace.query.count()
    
    # Estimativa de MRR (Monthly Recurring Revenue)
    pro_users = User.query.filter_by(subscription_plan='pro').count()
    business_users = User.query.filter_by(subscription_plan='business').count()
    mrr = (pro_users * 49) + (business_users * 99)
    
    stats = {
        'total_users': total_users,
        'new_users': new_users,
        'active_subs': active_subs,
        'mrr': f"{mrr:,.2f}",
        'total_projects': total_projects,
        'active_workspaces': active_workspaces
    }
    
    # Buscar últimos 10 usuários
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    
    return render_template('admin_dashboard.html', stats=stats, recent_users=recent_users)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    plan = request.args.get('plan', '')
    
    query = User.query
    
    if search:
        search_term = f"%{search}%"
        query = query.filter((User.username.ilike(search_term)) | (User.email.ilike(search_term)) | (User.full_name.ilike(search_term)))
    
    if plan:
        query = query.filter(User.subscription_plan == plan)
        
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/<int:user_id>/toggle_status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Você não pode desativar a si mesmo!', 'danger')
        return redirect(url_for('admin_users'))
        
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "ativado" if user.is_active else "desativado"
    flash(f'Usuário {user.username} {status} com sucesso.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/financial')
@login_required
@admin_required
def admin_financial():
    # Placeholder for Financial Page
    return render_template('admin_financial.html')

@app.route('/admin/settings')
@login_required
@admin_required
def admin_settings():
    # Placeholder for Settings Page
    return render_template('admin_settings.html')
# ==================== ADMIN API ====================


@app.route('/api/admin/overview', methods=['GET'])
@admin_required
def api_admin_overview():
    now = datetime.utcnow()
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'new_users': User.query.filter(User.created_at >= (now - timedelta(days=30))).count(),
        'admin_users': User.query.filter_by(is_admin=True).count(),
        'paid_users': User.query.filter(User.subscription_plan != 'free').count()
    }
    plans = get_active_plans(include_inactive=True)
    lookup = {plan.slug: plan.name for plan in plans}
    plan_counts = db.session.query(User.subscription_plan, func.count(User.id)).group_by(User.subscription_plan).all()
    plan_usage = [
        {
            'label': lookup.get(slug, slug.capitalize() if slug else 'Não definido'),
            'value': count
        }
        for slug, count in plan_counts
    ]
    return jsonify({'stats': stats, 'plan_usage': plan_usage})


@app.route('/api/admin/users', methods=['GET'])
@admin_required
def api_admin_users():
    query = User.query
    search = request.args.get('search')
    if search:
        like = f"%{search}%"
        query = query.filter(or_(
            User.username.ilike(like),
            User.email.ilike(like),
            User.full_name.ilike(like)
        ))
    plan_filter = request.args.get('plan')
    if plan_filter:
        query = query.filter(User.subscription_plan == plan_filter)
    status = request.args.get('status')
    if status == 'active':
        query = query.filter(User.is_active.is_(True))
    elif status == 'inactive':
        query = query.filter(User.is_active.is_(False))

    users = query.order_by(User.created_at.desc()).all()
    return jsonify([user.to_dict() for user in users])


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def api_admin_update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    if 'is_admin' in data:
        user.is_admin = bool(data['is_admin'])

    if 'is_active' in data:
        if user.id == current_user.id and data['is_active'] is False:
            return jsonify({'error': 'Você não pode desativar sua própria conta'}), 400
        user.is_active = bool(data['is_active'])

    if 'subscription_plan' in data:
        plan = SubscriptionPlan.query.filter_by(slug=data['subscription_plan']).first()
        if not plan:
            return jsonify({'error': 'Plano inválido'}), 400
        user.subscription_plan = plan.slug

    if 'subscription_status' in data:
        user.subscription_status = data['subscription_status']

    db.session.commit()
    return jsonify(user.to_dict())


@app.route('/api/admin/plans', methods=['GET', 'POST'])
@admin_required
def api_admin_plans():
    if request.method == 'GET':
        plans = get_active_plans(include_inactive=True)
        return jsonify([plan.to_dict() for plan in plans])

    data = request.get_json() or {}
    slug = (data.get('slug') or '').lower()
    if not slug:
        return jsonify({'error': 'Slug é obrigatório'}), 400
    if SubscriptionPlan.query.filter_by(slug=slug).first():
        return jsonify({'error': 'Slug já utilizado'}), 400

    plan = SubscriptionPlan(
        name=data.get('name') or slug.title(),
        slug=slug,
        description=data.get('description'),
        badge_text=data.get('badge_text'),
        highlight=bool(data.get('highlight', False)),
        is_default=bool(data.get('is_default', False)),
        order=int(data.get('order', 0)),
        price_monthly=parse_float(data.get('price_monthly'), 0) or 0,
        price_yearly=parse_float(data.get('price_yearly')),
        currency=data.get('currency', 'BRL'),
        stripe_price_monthly_id=data.get('stripe_price_monthly_id'),
        stripe_price_yearly_id=data.get('stripe_price_yearly_id'),
        features=normalize_features(data.get('features', [])),
        is_active=bool(data.get('is_active', True))
    )

    if plan.price_yearly is None:
        monthly = plan.price_monthly or 0
        plan.price_yearly = round(monthly * 12 * 0.8, 2) if monthly else 0

    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201


@app.route('/api/admin/plans/<int:plan_id>', methods=['PUT', 'DELETE'])
@admin_required
def api_admin_update_plan(plan_id):
    plan = SubscriptionPlan.query.get_or_404(plan_id)

    if request.method == 'DELETE':
        plan.is_active = False
        db.session.commit()
        return jsonify({'success': True})

    data = request.get_json() or {}
    if 'name' in data:
        plan.name = data['name']
    if 'description' in data:
        plan.description = data['description']
    if 'badge_text' in data:
        plan.badge_text = data['badge_text']
    if 'highlight' in data:
        plan.highlight = bool(data['highlight'])
    if 'is_default' in data:
        plan.is_default = bool(data['is_default'])
    if 'order' in data:
        plan.order = int(data['order'])
    if 'price_monthly' in data:
        plan.price_monthly = parse_float(data['price_monthly'], plan.price_monthly) or 0
    if 'price_yearly' in data:
        plan.price_yearly = parse_float(data['price_yearly'], plan.price_yearly)
    if 'currency' in data:
        plan.currency = data['currency']
    if 'stripe_price_monthly_id' in data:
        plan.stripe_price_monthly_id = data['stripe_price_monthly_id']
    if 'stripe_price_yearly_id' in data:
        plan.stripe_price_yearly_id = data['stripe_price_yearly_id']
    if 'is_active' in data:
        plan.is_active = bool(data['is_active'])
    if 'features' in data:
        plan.features = normalize_features(data['features'])

    if plan.price_yearly is None:
        monthly = plan.price_monthly or 0
        plan.price_yearly = round(monthly * 12 * 0.8, 2) if monthly else 0

    db.session.commit()
    return jsonify(plan.to_dict())


def serialize_setting(setting):
    payload = setting.to_dict(include_value=not setting.is_secret)
    if setting.is_secret:
        payload['value'] = ''
        payload['masked_value'] = '••••••' if setting.value else ''
    else:
        payload['value'] = setting.value
    return payload


@app.route('/api/admin/settings', methods=['GET'])
@admin_required
def api_admin_settings():
    settings = SystemSetting.query.order_by(SystemSetting.category.asc(), SystemSetting.key.asc()).all()
    return jsonify([serialize_setting(setting) for setting in settings])


@app.route('/api/admin/settings/<string:key>', methods=['PUT'])
@admin_required
def api_admin_update_setting(key):
    setting = SystemSetting.query.filter_by(key=key).first_or_404()
    data = request.get_json() or {}
    value = data.get('value')
    if setting.is_secret and not value and not data.get('clear'):
        return jsonify({'error': 'Informe um valor para esta chave'}), 400
    if data.get('clear'):
        setting.value = None
    else:
        setting.value = value

    db.session.commit()
    apply_runtime_setting(setting.key, setting.value)
    return jsonify(serialize_setting(setting))


# ==================== SOCKETIO EVENTS ====================

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('user_joined', {'username': current_user.username}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('user_left', {'username': current_user.username}, room=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    message = Message(
        content=data['message'],
        sender_id=current_user.id,
        workspace_id=data.get('workspace_id'),
        project_id=data.get('project_id')
    )
    db.session.add(message)
    db.session.commit()
    
    emit('new_message', {
        'id': message.id,
        'content': message.content,
        'sender': current_user.to_dict(),
        'created_at': message.created_at.isoformat()
    }, room=room)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# ==================== CLI COMMANDS ====================

@app.cli.command()
def init_db():
    """Inicializar banco de dados"""
    db.create_all()
    ensure_default_data()
    print('Banco de dados inicializado!')

@app.cli.command()
def create_admin():
    """Criar usuário admin"""
    db.create_all()
    ensure_default_data()
    admin = User.query.filter_by(username='thiagolobo').first()
    if admin:
        print('Usuário admin já existe!')
        return
    
    admin = User(
        username='thiagolobo',
        email='thiago@taskflowai.com',
        full_name='Thiago Lobo',
        is_admin=True
    )
    admin.set_password('#Wolf@1902')
    
    db.session.add(admin)
    db.session.commit()
    
    # Criar workspace padrão
    workspace = Workspace(
        name='Workspace Admin',
        slug='admin-workspace',
        owner_id=admin.id
    )
    db.session.add(workspace)
    workspace.members.append(admin)
    db.session.commit()
    
    print('Usuário admin criado com sucesso!')
    print('Username: thiagolobo')
    print('Password: #Wolf@1902')

@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "app": "TaskFlowAI", "version": "1.0.0"})


# ==========================================
# RITUAL OS ROUTES
# ==========================================

@app.route('/ritual')
@login_required
def ritual_dashboard():
    return render_template('ritual_dashboard.html', user=current_user)

@app.route('/api/ritual/generate', methods=['POST'])
@login_required
def generate_ritual():
    data = request.json
    goal_title = data.get('goal')
    pillar = data.get('pillar', 'general')
    
    if not goal_title:
        return jsonify({"error": "Goal required"}), 400
        
    # LIMIT CHECK (Free Plan)
    if current_user.subscription_plan == 'free':
        active_goals_count = Goal.query.filter_by(user_id=current_user.id, status='active').count()
        if active_goals_count >= 1:
            return jsonify({
                "error": "Limite atingido",
                "message": "O plano gratuito permite apenas 1 ritual ativo. Faça upgrade para ilimitado."
            }), 403
            
    # 1. Criar Goal
    new_goal = Goal(
        title=goal_title,
        pillar=pillar,
        user_id=current_user.id
    )
    db.session.add(new_goal)
    db.session.commit()
    
    # 2. Gerar System via AI
    try:
        ai = AIService(os.getenv('OPENAI_API_KEY'))
        system_data = ai.generate_ritual_system(goal_title, pillar)
    except Exception as e:
        print(f"ERROR GENERATING RITUAL: {e}")
        # Fallback to simple default if AI fails
        system_data = {
            'system_title': f"Ritual: {goal_title}",
            'description': "Ritual criado automaticamente (Modo Fallback)",
            'frequency': 'daily',
            'time_of_day': 'morning',
            'micro_actions': [
                {
                    'action_ideal': f"Trabalhar em {goal_title} por 20min",
                    'action_bad_day': f"Pensar em {goal_title} por 1min",
                    'duration_minutes': 20
                }
            ]
        }
    
    # 3. Salvar System
    new_system = System(
        title=system_data.get('system_title', f"Ritual: {goal_title}"),
        description=system_data.get('description'),
        frequency=system_data.get('frequency', 'daily'),
        time_of_day=system_data.get('time_of_day', 'morning'),
        goal_id=new_goal.id
    )
    db.session.add(new_system)
    db.session.commit()
    
    # 4. Salvar MicroActions
    for ma in system_data.get('micro_actions', []):
        micro = MicroAction(
            system_id=new_system.id,
            action_ideal=ma.get('action_ideal'),
            action_bad_day=ma.get('action_bad_day'),
            duration_minutes=ma.get('duration_minutes', 15)
        )
        db.session.add(micro)
    
    db.session.commit()
    
    return jsonify({"status": "success", "system_id": new_system.id})

@app.route('/api/ritual/complete', methods=['POST'])
@login_required
def complete_ritual():
    data = request.json
    action_id = data.get('action_id')
    mood = data.get('mood', 'normal')
    
    if not action_id:
        return jsonify({"error": "Action ID required"}), 400
        
    # Verificar se já completou hoje
    today = datetime.utcnow().date()
    existing_log = DailyLog.query.filter_by(user_id=current_user.id, date=today).first()
    
    if not existing_log:
        existing_log = DailyLog(user_id=current_user.id, date=today, mood=mood)
        db.session.add(existing_log)
        db.session.commit()
    
    # Verificar se ação já foi completada neste log
    existing_completion = CompletedAction.query.filter_by(
        daily_log_id=existing_log.id,
        micro_action_id=action_id
    ).first()
    
    if existing_completion:
        return jsonify({"message": "Already completed", "status": "exists"})
        
    # Registrar ação
    version = 'bad_day' if mood == 'hard' else 'ideal'
    completion = CompletedAction(
        daily_log_id=existing_log.id,
        micro_action_id=action_id,
        version_completed=version
    )
    db.session.add(completion)
    db.session.commit()
    
    return jsonify({"status": "success", "streak": 1}) # TODO: Return real streak

@app.route('/api/ritual/systems', methods=['GET'])
@login_required
def get_rituals():
    # Retorna os sistemas do usuário para o dia
    goals = Goal.query.filter_by(user_id=current_user.id, status='active').all()
    rituals = []
    
    # Cache do log de hoje
    today = datetime.utcnow().date()
    daily_log = DailyLog.query.filter_by(user_id=current_user.id, date=today).first()
    completed_ids = []
    if daily_log:
        completed_ids = [c.micro_action_id for c in daily_log.completed_actions]
    
    for goal in goals:
        for system in goal.systems:
            streak = system.get_current_streak()
            for action in system.micro_actions:
                rituals.append({
                    "id": action.id,
                    "goal_title": goal.title,
                    "system_title": system.title,
                    "action_ideal": action.action_ideal,
                    "action_bad_day": action.action_bad_day,
                    "duration_minutes": action.duration_minutes,
                    "completed": action.id in completed_ids,
                    "streak": streak
                })
                
    return jsonify(rituals)

@app.route('/api/ritual/stats', methods=['GET'])
@login_required
def get_ritual_stats():
    # Simples estatísticas de completamento nos últimos 7 dias
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=6)
    
    logs = DailyLog.query.filter(
        DailyLog.user_id == current_user.id,
        DailyLog.date >= start_date
    ).all()
    
    # Mapear data -> completados
    stats = {}
    current = start_date
    while current <= end_date:
        stats[current.isoformat()] = 0
        current += timedelta(days=1)
        
    for log in logs:
        stats[log.date.isoformat()] = len(log.completed_actions)
        
    return jsonify(stats)


# ==================== RUN ====================
@app.route('/api/ritual/insight', methods=['POST'])
@login_required
def ritual_insight():
    # 1. Coletar dados da última semana
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    
    logs = DailyLog.query.filter(
        DailyLog.user_id == current_user.id,
        DailyLog.date >= week_ago
    ).all()
    
    # Simple aggregations
    stats = {}
    for log in logs:
        date_str = log.date.strftime('%Y-%m-%d')
        # Contar total de CompletedAction para esse log (assumindo que DailyLog é por dia)
        # Na verdade DailyLog é 1 por dia. Precisamos contar quantosCompletedAction existem nesse dia?
        # daily_log_id não está em completed_action, mas completed_action tem completed_at.
        # Vamos usar a logica do get_ritual_stats que já retorna o heatmap.
        pass
        
    # Reusing the existing stats logic for simplicity
    raw_stats = {}
    current_date = week_ago
    while current_date <= today:
        count = db.session.query(CompletedAction)\
            .join(DailyLog, CompletedAction.daily_log_id == DailyLog.id)\
            .filter(DailyLog.user_id == current_user.id)\
            .filter(DailyLog.date == current_date)\
            .count()
        raw_stats[current_date.strftime('%Y-%m-%d')] = count
        current_date += timedelta(days=1)
            
    # 2. Chamar AI
    ai = AIService(os.getenv('OPENAI_API_KEY'))
    insight_text = ai.generate_kaizen_insight(raw_stats)
    
    return jsonify({"insight": insight_text})

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    domain_url = request.host_url
    price_id = request.form.get('priceId')
    
    # Fallback for demo if no specific price sent, use a default Pro ID
    if not price_id:
        price_id = os.getenv('STRIPE_PRICE_ID_PRO', 'price_H5ggYJDqNyCc3p') 

    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + 'settings?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + 'pricing',
            payment_method_types=['card'],
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            customer_email=current_user.email,
            client_reference_id=str(current_user.id),
            metadata={
                'user_id': current_user.id
            }
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/create-portal-session', methods=['POST'])
@login_required
def create_portal_session():
    domain_url = request.host_url
    
    # We need the stripe_customer_id saved on the user. 
    # If not present (legacy user), we can't open portal easily without logic to find/create.
    # For MVP, assuming new subs have it.
    
    # Mock for users without stripe_id to not crash
    if not current_user.stripe_customer_id:
        flash("Você ainda não tem uma assinatura ativa para gerenciar.", "warning")
        return redirect(url_for('subscription_settings'))

    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=domain_url + 'settings',
        )
        return redirect(portal_session.url, code=303)
    except Exception as e:
        return jsonify(error=str(e)), 403

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_default_data()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
