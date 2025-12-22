from backend.database import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(200))
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(500))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relacionamentos
    workspaces = db.relationship('Workspace', secondary='workspace_member', back_populates='members')
    created_workspaces = db.relationship('Workspace', back_populates='owner', foreign_keys='Workspace.owner_id')
    assigned_tasks = db.relationship('Task', secondary='task_assignment', back_populates='assigned_users')
    comments = db.relationship('Comment', back_populates='author')
    subscription = db.relationship('Subscription', back_populates='user', uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'avatar_url': self.avatar_url,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Workspace(db.Model):
    __tablename__ = 'workspace'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    icon = db.Column(db.String(100))
    color = db.Column(db.String(7), default='#1E64F0')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    owner = db.relationship('User', back_populates='created_workspaces', foreign_keys=[owner_id])
    members = db.relationship('User', secondary='workspace_member', back_populates='workspaces')
    spaces = db.relationship('Space', back_populates='workspace', cascade='all, delete-orphan')
    projects = db.relationship('Project', back_populates='workspace', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'owner_id': self.owner_id,
            'icon': self.icon,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class WorkspaceMember(db.Model):
    __tablename__ = 'workspace_member'
    
    id = db.Column(db.Integer, primary_key=True)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # owner, admin, member, guest
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)


class Space(db.Model):
    __tablename__ = 'space'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    icon = db.Column(db.String(100))
    color = db.Column(db.String(7))
    is_private = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    workspace = db.relationship('Workspace', back_populates='spaces')
    projects = db.relationship('Project', back_populates='space', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'workspace_id': self.workspace_id,
            'icon': self.icon,
            'color': self.color,
            'is_private': self.is_private
        }


class Project(db.Model):
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'))
    status = db.Column(db.String(20), default='active')  # active, archived, completed
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    color = db.Column(db.String(7))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    workspace = db.relationship('Workspace', back_populates='projects')
    space = db.relationship('Space', back_populates='projects')
    lists = db.relationship('List', back_populates='project', cascade='all, delete-orphan')
    tasks = db.relationship('Task', back_populates='project', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'workspace_id': self.workspace_id,
            'space_id': self.space_id,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'color': self.color,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class List(db.Model):
    __tablename__ = 'list'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    position = db.Column(db.Integer, default=0)
    color = db.Column(db.String(7))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    project = db.relationship('Project', back_populates='lists')
    tasks = db.relationship('Task', back_populates='list', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'project_id': self.project_id,
            'position': self.position,
            'color': self.color
        }


class Task(db.Model):
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey('list.id'))
    parent_task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    status = db.Column(db.String(20), default='to_do')  # to_do, in_progress, completed, archived
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent
    due_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    position = db.Column(db.Integer, default=0)
    time_estimate = db.Column(db.Integer)  # em minutos
    time_spent = db.Column(db.Integer, default=0)  # em minutos
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    project = db.relationship('Project', back_populates='tasks')
    list = db.relationship('List', back_populates='tasks')
    parent_task = db.relationship('Task', remote_side=[id], backref='subtasks')
    assigned_users = db.relationship('User', secondary='task_assignment', back_populates='assigned_tasks')
    comments = db.relationship('Comment', back_populates='task', cascade='all, delete-orphan')
    attachments = db.relationship('Attachment', back_populates='task', cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary='task_tag', back_populates='tasks')
    checklist_items = db.relationship('ChecklistItem', back_populates='task', cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'project_id': self.project_id,
            'list_id': self.list_id,
            'parent_task_id': self.parent_task_id,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'position': self.position,
            'time_estimate': self.time_estimate,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_details:
            data['assigned_users'] = [u.to_dict() for u in self.assigned_users]
            data['tags'] = [t.to_dict() for t in self.tags]
            data['comments_count'] = len(self.comments)
            data['attachments_count'] = len(self.attachments)
            data['subtasks_count'] = len(self.subtasks)
        
        return data


class TaskAssignment(db.Model):
    __tablename__ = 'task_assignment'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)


class Tag(db.Model):
    __tablename__ = 'tag'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), default='#5AE4C3')
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'))
    
    # Relacionamentos
    tasks = db.relationship('Task', secondary='task_tag', back_populates='tags')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color
        }


class TaskTag(db.Model):
    __tablename__ = 'task_tag'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)


class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    task = db.relationship('Task', back_populates='comments')
    author = db.relationship('User', back_populates='comments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'task_id': self.task_id,
            'author': self.author.to_dict() if self.author else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Attachment(db.Model):
    __tablename__ = 'attachment'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(500), nullable=False)
    file_path = db.Column(db.String(1000), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    task = db.relationship('Task', back_populates='attachments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }


class ChecklistItem(db.Model):
    __tablename__ = 'checklist_item'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    task = db.relationship('Task', back_populates='checklist_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'is_completed': self.is_completed,
            'position': self.position
        }


class Document(db.Model):
    __tablename__ = 'document'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'workspace_id': self.workspace_id,
            'project_id': self.project_id,
            'author_id': self.author_id,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    workspace_id = db.Column(db.Integer, db.ForeignKey('workspace.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # para mensagens privadas
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'workspace_id': self.workspace_id,
            'project_id': self.project_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
