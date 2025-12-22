import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json
from functools import wraps
from sqlalchemy import or_, func

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
    SystemSetting
)
from ai_service import AIService

# Inicializar Flask
app = Flask(__name__)
app.config.from_object(config[os.environ.get('FLASK_ENV', 'development')])

# Configurar para funcionar em subpath /taskflowai
app.config['APPLICATION_ROOT'] = '/taskflowai'

# Criar diretórios necessários
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/avatars', exist_ok=True)

# Inicializar extensões
db.init_app(app)
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
        'key': 'STRIPE_PUBLIC_KEY',
        'category': 'payments',
        'description': 'Chave pública utilizada no checkout Stripe.',
        'is_secret': True
    },
    {
        'key': 'STRIPE_SECRET_KEY',
        'category': 'payments',
        'description': 'Chave secreta utilizada para operações com Stripe.',
        'is_secret': True
    },
    {
        'key': 'STRIPE_WEBHOOK_SECRET',
        'category': 'payments',
        'description': 'Webhook secret da Stripe.',
        'is_secret': True
    }
]

RUNTIME_SETTING_MAP = {
    'OPENAI_API_KEY': 'OPENAI_API_KEY',
    'STRIPE_PUBLIC_KEY': 'STRIPE_PUBLIC_KEY',
    'STRIPE_SECRET_KEY': 'STRIPE_SECRET_KEY',
    'STRIPE_WEBHOOK_SECRET': 'STRIPE_WEBHOOK_SECRET'
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


@app.before_first_request
def bootstrap_defaults():
    db.create_all()
    ensure_default_data()

# ==================== ROTAS PÚBLICAS ====================

@app.route('/')
def index():
    """Landing page"""
    if current_user.is_authenticated:
        return redirect('/taskflowai/dashboard')
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect('/taskflowai/dashboard')
    
    if request.method == 'POST':
        data = request.form if request.form else request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user and user.check_password(password):
            login_user(user, remember=data.get('remember', False))
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': 'Login realizado com sucesso',
                    'redirect': '/taskflowai/dashboard'
                })
            return redirect('/taskflowai/dashboard')
        
        if request.is_json:
            return jsonify({'success': False, 'message': 'Usuário ou senha inválidos'}), 401
        flash('Usuário ou senha inválidos', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
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
                flash(f'Convite aceito! Você agora participa do workspace {target_workspace.name}', 'success')
        
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
    """Dashboard principal"""
    member_workspaces = list(current_user.workspaces)
    owned_workspaces = list(current_user.owned_workspaces)
    workspace_options = list({w.id: w for w in (member_workspaces + owned_workspaces)}.values())
    workspaces = workspace_options
    workspace_ids = [w.id for w in workspace_options]
    projects = []
    if workspace_ids:
        projects = Project.query.filter(
            Project.workspace_id.in_(workspace_ids),
            Project.is_active == True
        ).order_by(Project.name.asc()).all()
    
    # Estatísticas rápidas
    total_tasks = Task.query.filter_by(creator_id=current_user.id).count()
    completed_tasks = Task.query.filter_by(creator_id=current_user.id, status='done').count()
    assigned_tasks = len(current_user.assigned_tasks)
    
    stats = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'assigned_tasks': assigned_tasks,
        'pending_tasks': assigned_tasks - completed_tasks
    }
    
    # Tarefas recentes
    recent_tasks = Task.query.filter_by(creator_id=current_user.id)\
        .order_by(Task.created_at.desc()).limit(10).all()
    
    # Notificações não lidas
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False)\
        .order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         workspaces=workspaces,
                         workspace_options=workspace_options,
                         projects=projects,
                         stats=stats,
                         recent_tasks=recent_tasks,
                         notifications=notifications)

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
        'paid_users': User.query.filter(User.subscription_plan != 'free').count()
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

# ==================== API ENDPOINTS ====================

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

# ==================== RUN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_default_data()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
