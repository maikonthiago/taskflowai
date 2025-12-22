import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import json

from config import config
from models import db, User, Workspace, Space, Project, TaskList, Task, Comment, Attachment, Message, Notification
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
        
        login_user(user)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Conta criada com sucesso',
                'redirect': '/taskflowai/dashboard'
            })
        
        flash('Conta criada com sucesso!', 'success')
        return redirect('/taskflowai/dashboard')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect('/taskflowai/')

@app.route('/pricing')
def pricing():
    """Página de preços"""
    plans = app.config['PLANS']
    return render_template('pricing.html', plans=plans)

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    workspaces = current_user.workspaces
    if not workspaces:
        workspaces = current_user.owned_workspaces
    
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
    return render_template('subscription.html', user=current_user, plans=app.config['PLANS'])

# ==================== API ENDPOINTS ====================

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
        task = Task(
            title=data['title'],
            description=data.get('description'),
            project_id=data['project_id'],
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
    
    try:
        tasks_data = ai_service.generate_tasks_from_description(description)
        
        # Criar tarefas no banco
        created_tasks = []
        for task_data in tasks_data:
            task = Task(
                title=task_data['title'],
                description=task_data.get('description'),
                project_id=project_id,
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
    print('Banco de dados inicializado!')

@app.cli.command()
def create_admin():
    """Criar usuário admin"""
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
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
