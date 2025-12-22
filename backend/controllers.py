"""
Controllers for TaskFlowAI Flask Application
Handles business logic for all API endpoints
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import and_, or_
from sqlalchemy.exc import SQLAlchemyError

from backend.models import (
    db, User, Workspace, WorkspaceMember, Project, 
    Space, TaskList, Task, TaskAssignment, Comment, 
    Document, ChatMessage
)
from backend.models_finance import (
    FinancialAccount, FinancialTransaction, 
    FinancialCategory, Budget
)

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24


# ============================================================================
# AUTHENTICATION CONTROLLERS
# ============================================================================

def register_user(username: str, email: str, password: str, full_name: str = None) -> Dict[str, Any]:
    """
    Register a new user with hashed password
    
    Args:
        username: Unique username
        email: User email address
        password: Plain text password (will be hashed)
        full_name: Optional full name
        
    Returns:
        Dict with user data or error message
    """
    try:
        # Check if user already exists
        existing_user = User.query.filter(
            or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            return {
                'success': False,
                'error': 'Username or email already exists'
            }
        
        # Hash password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return {
            'success': True,
            'user': {
                'id': new_user.id,
                'username': new_user.username,
                'email': new_user.email,
                'full_name': new_user.full_name
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def login_user(identifier: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user and generate JWT token
    
    Args:
        identifier: Username or email
        password: Plain text password
        
    Returns:
        Dict with JWT token and user data or error message
    """
    try:
        # Find user by username or email
        user = User.query.filter(
            or_(User.username == identifier, User.email == identifier)
        ).first()
        
        if not user:
            return {
                'success': False,
                'error': 'Invalid credentials'
            }
        
        if not user.is_active:
            return {
                'success': False,
                'error': 'Account is inactive'
            }
        
        # Verify password
        if not check_password_hash(user.password_hash, password):
            return {
                'success': False,
                'error': 'Invalid credentials'
            }
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate JWT token
        token_payload = {
            'user_id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)
        }
        token = jwt.encode(token_payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
        
        return {
            'success': True,
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def get_current_user(token: str) -> Dict[str, Any]:
    """
    Decode JWT token and return user data
    
    Args:
        token: JWT token string
        
    Returns:
        Dict with user data or error message
    """
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        
        if not user_id:
            return {
                'success': False,
                'error': 'Invalid token payload'
            }
        
        # Get user from database
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return {
                'success': False,
                'error': 'User not found or inactive'
            }
        
        return {
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
        }
        
    except jwt.ExpiredSignatureError:
        return {
            'success': False,
            'error': 'Token has expired'
        }
    except jwt.InvalidTokenError:
        return {
            'success': False,
            'error': 'Invalid token'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


# ============================================================================
# WORKSPACE CONTROLLERS
# ============================================================================

def create_workspace(name: str, description: str, owner_id: int) -> Dict[str, Any]:
    """
    Create a new workspace
    
    Args:
        name: Workspace name
        description: Workspace description
        owner_id: ID of the workspace owner
        
    Returns:
        Dict with workspace data or error message
    """
    try:
        # Verify owner exists
        owner = User.query.get(owner_id)
        if not owner:
            return {
                'success': False,
                'error': 'Owner user not found'
            }
        
        # Create workspace
        workspace = Workspace(
            name=name,
            description=description,
            owner_id=owner_id
        )
        
        db.session.add(workspace)
        db.session.flush()  # Get workspace ID
        
        # Add owner as admin member
        member = WorkspaceMember(
            workspace_id=workspace.id,
            user_id=owner_id,
            role='admin'
        )
        
        db.session.add(member)
        db.session.commit()
        
        return {
            'success': True,
            'workspace': {
                'id': workspace.id,
                'name': workspace.name,
                'description': workspace.description,
                'owner_id': workspace.owner_id,
                'created_at': workspace.created_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def get_workspaces(user_id: int) -> Dict[str, Any]:
    """
    Get all workspaces for a user
    
    Args:
        user_id: User ID
        
    Returns:
        Dict with list of workspaces
    """
    try:
        # Get workspaces where user is a member
        memberships = WorkspaceMember.query.filter_by(user_id=user_id).all()
        workspace_ids = [m.workspace_id for m in memberships]
        
        workspaces = Workspace.query.filter(Workspace.id.in_(workspace_ids)).all()
        
        workspace_list = []
        for workspace in workspaces:
            # Get user's role
            member = next((m for m in memberships if m.workspace_id == workspace.id), None)
            
            workspace_list.append({
                'id': workspace.id,
                'name': workspace.name,
                'description': workspace.description,
                'owner_id': workspace.owner_id,
                'role': member.role if member else None,
                'created_at': workspace.created_at.isoformat(),
                'updated_at': workspace.updated_at.isoformat() if workspace.updated_at else None
            })
        
        return {
            'success': True,
            'workspaces': workspace_list
        }
        
    except SQLAlchemyError as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def update_workspace(workspace_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update workspace details
    
    Args:
        workspace_id: Workspace ID
        data: Dictionary with fields to update
        
    Returns:
        Dict with updated workspace data
    """
    try:
        workspace = Workspace.query.get(workspace_id)
        
        if not workspace:
            return {
                'success': False,
                'error': 'Workspace not found'
            }
        
        # Update fields
        if 'name' in data:
            workspace.name = data['name']
        if 'description' in data:
            workspace.description = data['description']
        
        workspace.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'workspace': {
                'id': workspace.id,
                'name': workspace.name,
                'description': workspace.description,
                'updated_at': workspace.updated_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def delete_workspace(workspace_id: int) -> Dict[str, Any]:
    """
    Delete a workspace and all related data
    
    Args:
        workspace_id: Workspace ID
        
    Returns:
        Dict with success status
    """
    try:
        workspace = Workspace.query.get(workspace_id)
        
        if not workspace:
            return {
                'success': False,
                'error': 'Workspace not found'
            }
        
        # Delete related data (cascade should handle most)
        db.session.delete(workspace)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Workspace deleted successfully'
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def add_member(workspace_id: int, user_id: int, role: str = 'member') -> Dict[str, Any]:
    """
    Add a member to a workspace
    
    Args:
        workspace_id: Workspace ID
        user_id: User ID to add
        role: Role (admin, member, viewer)
        
    Returns:
        Dict with success status
    """
    try:
        # Verify workspace exists
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            return {
                'success': False,
                'error': 'Workspace not found'
            }
        
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            return {
                'success': False,
                'error': 'User not found'
            }
        
        # Check if already a member
        existing = WorkspaceMember.query.filter_by(
            workspace_id=workspace_id,
            user_id=user_id
        ).first()
        
        if existing:
            return {
                'success': False,
                'error': 'User is already a member'
            }
        
        # Add member
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role
        )
        
        db.session.add(member)
        db.session.commit()
        
        return {
            'success': True,
            'member': {
                'id': member.id,
                'user_id': member.user_id,
                'workspace_id': member.workspace_id,
                'role': member.role,
                'joined_at': member.joined_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


# ============================================================================
# PROJECT CONTROLLERS
# ============================================================================

def create_project(name: str, description: str, workspace_id: int, 
                  space_id: int = None) -> Dict[str, Any]:
    """
    Create a new project
    
    Args:
        name: Project name
        description: Project description
        workspace_id: Workspace ID
        space_id: Optional space ID
        
    Returns:
        Dict with project data
    """
    try:
        # Verify workspace exists
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            return {
                'success': False,
                'error': 'Workspace not found'
            }
        
        # Verify space if provided
        if space_id:
            space = Space.query.get(space_id)
            if not space or space.workspace_id != workspace_id:
                return {
                    'success': False,
                    'error': 'Invalid space for this workspace'
                }
        
        # Create project
        project = Project(
            name=name,
            description=description,
            workspace_id=workspace_id,
            space_id=space_id,
            status='active'
        )
        
        db.session.add(project)
        db.session.commit()
        
        return {
            'success': True,
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'workspace_id': project.workspace_id,
                'space_id': project.space_id,
                'status': project.status,
                'created_at': project.created_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def get_projects(workspace_id: int, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get projects with optional filters
    
    Args:
        workspace_id: Workspace ID
        filters: Optional dict with status, space_id, etc.
        
    Returns:
        Dict with list of projects
    """
    try:
        query = Project.query.filter_by(workspace_id=workspace_id)
        
        # Apply filters
        if filters:
            if 'status' in filters:
                query = query.filter_by(status=filters['status'])
            if 'space_id' in filters:
                query = query.filter_by(space_id=filters['space_id'])
        
        projects = query.order_by(Project.created_at.desc()).all()
        
        project_list = []
        for project in projects:
            project_list.append({
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'workspace_id': project.workspace_id,
                'space_id': project.space_id,
                'status': project.status,
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'created_at': project.created_at.isoformat(),
                'updated_at': project.updated_at.isoformat() if project.updated_at else None
            })
        
        return {
            'success': True,
            'projects': project_list
        }
        
    except SQLAlchemyError as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def update_project(project_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update project details
    
    Args:
        project_id: Project ID
        data: Dictionary with fields to update
        
    Returns:
        Dict with updated project data
    """
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found'
            }
        
        # Update fields
        if 'name' in data:
            project.name = data['name']
        if 'description' in data:
            project.description = data['description']
        if 'status' in data:
            project.status = data['status']
        if 'start_date' in data:
            project.start_date = datetime.fromisoformat(data['start_date']) if data['start_date'] else None
        if 'end_date' in data:
            project.end_date = datetime.fromisoformat(data['end_date']) if data['end_date'] else None
        
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'project': {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'status': project.status,
                'updated_at': project.updated_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def delete_project(project_id: int) -> Dict[str, Any]:
    """
    Delete a project
    
    Args:
        project_id: Project ID
        
    Returns:
        Dict with success status
    """
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return {
                'success': False,
                'error': 'Project not found'
            }
        
        db.session.delete(project)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Project deleted successfully'
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


# ============================================================================
# TASK CONTROLLERS
# ============================================================================

def create_task(title: str, description: str, project_id: int, list_id: int,
               assigned_users: List[int] = None, priority: str = 'medium',
               due_date: str = None) -> Dict[str, Any]:
    """
    Create a new task
    
    Args:
        title: Task title
        description: Task description
        project_id: Project ID
        list_id: Task list ID
        assigned_users: List of user IDs to assign
        priority: Task priority (low, medium, high, urgent)
        due_date: ISO format date string
        
    Returns:
        Dict with task data
    """
    try:
        # Verify project and list
        project = Project.query.get(project_id)
        if not project:
            return {
                'success': False,
                'error': 'Project not found'
            }
        
        task_list = TaskList.query.get(list_id)
        if not task_list or task_list.project_id != project_id:
            return {
                'success': False,
                'error': 'Invalid task list for this project'
            }
        
        # Create task
        task = Task(
            title=title,
            description=description,
            project_id=project_id,
            list_id=list_id,
            priority=priority,
            status='to_do',
            due_date=datetime.fromisoformat(due_date) if due_date else None
        )
        
        db.session.add(task)
        db.session.flush()  # Get task ID
        
        # Assign users
        if assigned_users:
            for user_id in assigned_users:
                user = User.query.get(user_id)
                if user:
                    assignment = TaskAssignment(
                        task_id=task.id,
                        user_id=user_id
                    )
                    db.session.add(assignment)
        
        db.session.commit()
        
        return {
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'project_id': task.project_id,
                'list_id': task.list_id,
                'priority': task.priority,
                'status': task.status,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'created_at': task.created_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def get_tasks(project_id: int, filters: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get tasks with optional filters
    
    Args:
        project_id: Project ID
        filters: Optional dict with status, priority, assigned_to, etc.
        
    Returns:
        Dict with list of tasks
    """
    try:
        query = Task.query.filter_by(project_id=project_id)
        
        # Apply filters
        if filters:
            if 'status' in filters:
                query = query.filter_by(status=filters['status'])
            if 'priority' in filters:
                query = query.filter_by(priority=filters['priority'])
            if 'list_id' in filters:
                query = query.filter_by(list_id=filters['list_id'])
            if 'assigned_to' in filters:
                # Join with assignments
                query = query.join(TaskAssignment).filter(
                    TaskAssignment.user_id == filters['assigned_to']
                )
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        task_list = []
        for task in tasks:
            # Get assigned users
            assignments = TaskAssignment.query.filter_by(task_id=task.id).all()
            assigned_user_ids = [a.user_id for a in assignments]
            
            task_list.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'project_id': task.project_id,
                'list_id': task.list_id,
                'priority': task.priority,
                'status': task.status,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'assigned_users': assigned_user_ids,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            })
        
        return {
            'success': True,
            'tasks': task_list
        }
        
    except SQLAlchemyError as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def update_task(task_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update task details
    
    Args:
        task_id: Task ID
        data: Dictionary with fields to update
        
    Returns:
        Dict with updated task data
    """
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return {
                'success': False,
                'error': 'Task not found'
            }
        
        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'completed':
                task.completed_at = datetime.utcnow()
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'updated_at': task.updated_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def delete_task(task_id: int) -> Dict[str, Any]:
    """
    Delete a task
    
    Args:
        task_id: Task ID
        
    Returns:
        Dict with success status
    """
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return {
                'success': False,
                'error': 'Task not found'
            }
        
        db.session.delete(task)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Task deleted successfully'
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def assign_user(task_id: int, user_id: int) -> Dict[str, Any]:
    """
    Assign a user to a task
    
    Args:
        task_id: Task ID
        user_id: User ID to assign
        
    Returns:
        Dict with success status
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            return {
                'success': False,
                'error': 'Task not found'
            }
        
        user = User.query.get(user_id)
        if not user:
            return {
                'success': False,
                'error': 'User not found'
            }
        
        # Check if already assigned
        existing = TaskAssignment.query.filter_by(
            task_id=task_id,
            user_id=user_id
        ).first()
        
        if existing:
            return {
                'success': False,
                'error': 'User already assigned to this task'
            }
        
        assignment = TaskAssignment(
            task_id=task_id,
            user_id=user_id
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        return {
            'success': True,
            'assignment': {
                'id': assignment.id,
                'task_id': assignment.task_id,
                'user_id': assignment.user_id,
                'assigned_at': assignment.assigned_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def update_status(task_id: int, status: str) -> Dict[str, Any]:
    """
    Update task status
    
    Args:
        task_id: Task ID
        status: New status (to_do, in_progress, completed, blocked)
        
    Returns:
        Dict with updated task data
    """
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return {
                'success': False,
                'error': 'Task not found'
            }
        
        task.status = status
        
        if status == 'completed':
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'task': {
                'id': task.id,
                'status': task.status,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'updated_at': task.updated_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


# ============================================================================
# COMMENT CONTROLLERS
# ============================================================================

def create_comment(task_id: int, author_id: int, content: str) -> Dict[str, Any]:
    """
    Create a comment on a task
    
    Args:
        task_id: Task ID
        author_id: User ID of comment author
        content: Comment content
        
    Returns:
        Dict with comment data
    """
    try:
        task = Task.query.get(task_id)
        if not task:
            return {
                'success': False,
                'error': 'Task not found'
            }
        
        author = User.query.get(author_id)
        if not author:
            return {
                'success': False,
                'error': 'Author not found'
            }
        
        comment = Comment(
            task_id=task_id,
            author_id=author_id,
            content=content
        )
        
        db.session.add(comment)
        db.session.commit()
        
        return {
            'success': True,
            'comment': {
                'id': comment.id,
                'task_id': comment.task_id,
                'author_id': comment.author_id,
                'content': comment.content,
                'created_at': comment.created_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def get_comments(task_id: int) -> Dict[str, Any]:
    """
    Get all comments for a task
    
    Args:
        task_id: Task ID
        
    Returns:
        Dict with list of comments
    """
    try:
        comments = Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.asc()).all()
        
        comment_list = []
        for comment in comments:
            author = User.query.get(comment.author_id)
            comment_list.append({
                'id': comment.id,
                'task_id': comment.task_id,
                'author_id': comment.author_id,
                'author_name': author.full_name or author.username if author else 'Unknown',
                'content': comment.content,
                'created_at': comment.created_at.isoformat(),
                'updated_at': comment.updated_at.isoformat() if comment.updated_at else None
            })
        
        return {
            'success': True,
            'comments': comment_list
        }
        
    except SQLAlchemyError as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def update_comment(comment_id: int, content: str) -> Dict[str, Any]:
    """
    Update comment content
    
    Args:
        comment_id: Comment ID
        content: New content
        
    Returns:
        Dict with updated comment data
    """
    try:
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return {
                'success': False,
                'error': 'Comment not found'
            }
        
        comment.content = content
        comment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'updated_at': comment.updated_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def delete_comment(comment_id: int) -> Dict[str, Any]:
    """
    Delete a comment
    
    Args:
        comment_id: Comment ID
        
    Returns:
        Dict with success status
    """
    try:
        comment = Comment.query.get(comment_id)
        
        if not comment:
            return {
                'success': False,
                'error': 'Comment not found'
            }
        
        db.session.delete(comment)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Comment deleted successfully'
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


# ============================================================================
# DOCUMENT CONTROLLERS
# ============================================================================

def create_document(title: str, content: str, workspace_id: int, 
                   author_id: int) -> Dict[str, Any]:
    """
    Create a document
    
    Args:
        title: Document title
        content: Document content
        workspace_id: Workspace ID
        author_id: Author user ID
        
    Returns:
        Dict with document data
    """
    try:
        workspace = Workspace.query.get(workspace_id)
        if not workspace:
            return {
                'success': False,
                'error': 'Workspace not found'
            }
        
        author = User.query.get(author_id)
        if not author:
            return {
                'success': False,
                'error': 'Author not found'
            }
        
        document = Document(
            title=title,
            content=content,
            workspace_id=workspace_id,
            author_id=author_id
        )
        
        db.session.add(document)
        db.session.commit()
        
        return {
            'success': True,
            'document': {
                'id': document.id,
                'title': document.title,
                'content': document.content,
                'workspace_id': document.workspace_id,
                'author_id': document.author_id,
                'created_at': document.created_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def get_documents(workspace_id: int) -> Dict[str, Any]:
    """
    Get all documents in a workspace
    
    Args:
        workspace_id: Workspace ID
        
    Returns:
        Dict with list of documents
    """
    try:
        documents = Document.query.filter_by(workspace_id=workspace_id).order_by(
            Document.updated_at.desc()
        ).all()
        
        document_list = []
        for doc in documents:
            author = User.query.get(doc.author_id)
            document_list.append({
                'id': doc.id,
                'title': doc.title,
                'content': doc.content,
                'workspace_id': doc.workspace_id,
                'author_id': doc.author_id,
                'author_name': author.full_name or author.username if author else 'Unknown',
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None
            })
        
        return {
            'success': True,
            'documents': document_list
        }
        
    except SQLAlchemyError as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def update_document(document_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update document
    
    Args:
        document_id: Document ID
        data: Dictionary with fields to update
        
    Returns:
        Dict with updated document data
    """
    try:
        document = Document.query.get(document_id)
        
        if not document:
            return {
                'success': False,
                'error': 'Document not found'
            }
        
        if 'title' in data:
            document.title = data['title']
        if 'content' in data:
            document.content = data['content']
        
        document.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'document': {
                'id': document.id,
                'title': document.title,
                'content': document.content,
                'updated_at': document.updated_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


# ============================================================================
# CHAT CONTROLLERS
# ============================================================================

def send_message(sender_id: int, content: str, workspace_id: int = None,
                project_id: int = None, recipient_id: int = None) -> Dict[str, Any]:
    """
    Send a chat message
    
    Args:
        sender_id: Sender user ID
        content: Message content
        workspace_id: Optional workspace ID (for workspace chat)
        project_id: Optional project ID (for project chat)
        recipient_id: Optional recipient ID (for direct message)
        
    Returns:
        Dict with message data
    """
    try:
        sender = User.query.get(sender_id)
        if not sender:
            return {
                'success': False,
                'error': 'Sender not found'
            }
        
        message = ChatMessage(
            sender_id=sender_id,
            content=content,
            workspace_id=workspace_id,
            project_id=project_id,
            recipient_id=recipient_id
        )
        
        db.session.add(message)
        db.session.commit()
        
        return {
            'success': True,
            'message': {
                'id': message.id,
                'sender_id': message.sender_id,
                'content': message.content,
                'workspace_id': message.workspace_id,
                'project_id': message.project_id,
                'recipient_id': message.recipient_id,
                'created_at': message.created_at.isoformat()
            }
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        db.session.rollback()
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }


def get_messages(workspace_id: int = None, project_id: int = None, 
                user_id: int = None) -> Dict[str, Any]:
    """
    Get chat messages with filters
    
    Args:
        workspace_id: Optional workspace ID filter
        project_id: Optional project ID filter
        user_id: Optional user ID filter (for direct messages)
        
    Returns:
        Dict with list of messages
    """
    try:
        query = ChatMessage.query
        
        if workspace_id:
            query = query.filter_by(workspace_id=workspace_id)
        
        if project_id:
            query = query.filter_by(project_id=project_id)
        
        if user_id:
            # Get direct messages to/from user
            query = query.filter(
                or_(
                    ChatMessage.sender_id == user_id,
                    ChatMessage.recipient_id == user_id
                )
            )
        
        messages = query.order_by(ChatMessage.created_at.asc()).all()
        
        message_list = []
        for msg in messages:
            sender = User.query.get(msg.sender_id)
            message_list.append({
                'id': msg.id,
                'sender_id': msg.sender_id,
                'sender_name': sender.full_name or sender.username if sender else 'Unknown',
                'content': msg.content,
                'workspace_id': msg.workspace_id,
                'project_id': msg.project_id,
                'recipient_id': msg.recipient_id,
                'created_at': msg.created_at.isoformat()
            })
        
        return {
            'success': True,
            'messages': message_list
        }
        
    except SQLAlchemyError as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }
