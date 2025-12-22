from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = SQLAlchemy()

# Tabelas de associação (Many-to-Many)
workspace_members = db.Table('workspace_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('workspace_id', db.Integer, db.ForeignKey('workspaces.id'), primary_key=True),
    db.Column('role', db.String(50), default='member'),  # owner, admin, member, viewer
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

project_members = db.Table('project_members',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id'), primary_key=True),
    db.Column('role', db.String(50), default='member')
)

task_assignees = db.Table('task_assignees',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('assigned_at', db.DateTime, default=datetime.utcnow)
)

task_tags = db.Table('task_tags',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    """Modelo de Usuário"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150))
    avatar = db.Column(db.String(255), default='default-avatar.png')
    bio = db.Column(db.Text)
    
    # Configurações
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    
    # Assinatura
    subscription_plan = db.Column(db.String(50), default='free')  # free, pro, business
    subscription_status = db.Column(db.String(50), default='active')  # active, canceled, past_due
    stripe_customer_id = db.Column(db.String(255))
    stripe_subscription_id = db.Column(db.String(255))
    subscription_end_date = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relacionamentos
    owned_workspaces = db.relationship('Workspace', backref='owner', lazy=True, foreign_keys='Workspace.owner_id')
    workspaces = db.relationship('Workspace', secondary=workspace_members, backref='members')
    created_tasks = db.relationship('Task', backref='creator', lazy=True, foreign_keys='Task.creator_id')
    assigned_tasks = db.relationship('Task', secondary=task_assignees, backref='assignees')
    comments = db.relationship('Comment', backref='author', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'avatar': self.avatar,
            'bio': self.bio,
            'is_admin': self.is_admin,
            'subscription_plan': self.subscription_plan,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Workspace(db.Model):
    """Workspace - Nível mais alto de organização"""
    __tablename__ = 'workspaces'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(150), unique=True, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='🏢')
    color = db.Column(db.String(7), default='#1E64F0')
    
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    spaces = db.relationship('Space', backref='workspace', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='workspace', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Space(db.Model):
    """Space - Agrupamento de projetos"""
    __tablename__ = 'spaces'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='📁')
    color = db.Column(db.String(7), default='#5AE4C3')
    
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    projects = db.relationship('Project', backref='space', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'workspace_id': self.workspace_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Project(db.Model):
    """Projeto"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='📋')
    color = db.Column(db.String(7), default='#1E64F0')
    
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('spaces.id'))
    
    # Datas
    start_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    
    # Status
    status = db.Column(db.String(50), default='active')  # active, on_hold, completed, archived
    progress = db.Column(db.Integer, default=0)  # 0-100
    
    is_active = db.Column(db.Boolean, default=True)
    is_private = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    lists = db.relationship('TaskList', backref='project', lazy=True, cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'workspace_id': self.workspace_id,
            'space_id': self.space_id,
            'status': self.status,
            'progress': self.progress,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class TaskList(db.Model):
    """Lista de tarefas"""
    __tablename__ = 'task_lists'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#5AE4C3')
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    position = db.Column(db.Integer, default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    tasks = db.relationship('Task', backref='task_list', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'project_id': self.project_id,
            'position': self.position,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Task(db.Model):
    """Tarefa"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    # Relacionamentos
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('task_lists.id'))
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))  # Para subtarefas
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Status e prioridade
    status = db.Column(db.String(50), default='todo')  # todo, in_progress, review, done
    priority = db.Column(db.String(50), default='medium')  # low, medium, high, urgent
    
    # Datas
    start_date = db.Column(db.DateTime)
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Estimativas
    estimated_hours = db.Column(db.Float)
    actual_hours = db.Column(db.Float, default=0)
    
    # Posição para ordenação
    position = db.Column(db.Integer, default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]), lazy=True)
    comments = db.relationship('Comment', backref='task', lazy=True, cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', backref='task', lazy=True, cascade='all, delete-orphan')
    checklists = db.relationship('Checklist', backref='task', lazy=True, cascade='all, delete-orphan')
    time_entries = db.relationship('TimeEntry', backref='task', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id,
            'list_id': self.list_id,
            'parent_task_id': self.parent_task_id,
            'creator_id': self.creator_id,
            'status': self.status,
            'priority': self.priority,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'position': self.position,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'assignees': [a.to_dict() for a in self.assignees]
        }


class Tag(db.Model):
    """Tags para organização"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(7), default='#5AE4C3')
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Comment(db.Model):
    """Comentários em tarefas"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    is_edited = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'task_id': self.task_id,
            'author': self.author.to_dict() if self.author else None,
            'is_edited': self.is_edited,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Attachment(db.Model):
    """Anexos"""
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Checklist(db.Model):
    """Checklist dentro de tarefas"""
    __tablename__ = 'checklists'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)
    
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)


class TimeEntry(db.Model):
    """Rastreamento de tempo"""
    __tablename__ = 'time_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255))
    hours = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Document(db.Model):
    """Documentos colaborativos"""
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Message(db.Model):
    """Mensagens do chat"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Para mensagens diretas
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])


class Notification(db.Model):
    """Notificações"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    type = db.Column(db.String(50))  # task_assigned, comment, mention, deadline, etc
    link = db.Column(db.String(500))
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'type': self.type,
            'link': self.link,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Automation(db.Model):
    """Automações"""
    __tablename__ = 'automations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    
    trigger_type = db.Column(db.String(50))  # task_created, task_completed, status_changed, etc
    trigger_conditions = db.Column(db.Text)  # JSON
    actions = db.Column(db.Text)  # JSON
    
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ActivityLog(db.Model):
    """Log de atividades"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))  # task, project, workspace, etc
    entity_id = db.Column(db.Integer)
    details = db.Column(db.Text)  # JSON
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspaces.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
