"""
TaskFlowAI - API Routes
Defines all API endpoints for the Flask application
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

# Import controllers
from backend.controllers import (
    # Auth controllers
    register_user,
    login_user,
    get_current_user,
    # Workspace controllers
    create_workspace,
    get_workspaces,
    get_workspace,
    update_workspace,
    delete_workspace,
    add_member,
    # Project controllers
    create_project,
    get_projects,
    get_project,
    update_project,
    delete_project,
    # Task controllers
    create_task,
    get_tasks,
    get_task,
    update_task,
    delete_task,
    assign_user,
    update_status,
    # Comment controllers
    create_comment,
    get_comments,
    update_comment,
    delete_comment,
    # Document controllers
    create_document,
    get_documents,
    update_document,
    # Chat controllers
    send_message,
    get_messages
)


def register_routes(app):
    """
    Register all API routes with the Flask application
    """

    # ==================== AUTH ROUTES ====================
    
    @app.route('/api/auth/register', methods=['POST'])
    def api_register():
        """Register a new user"""
        try:
            data = request.get_json()
            result = register_user(data)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/auth/login', methods=['POST'])
    def api_login():
        """Login user and return JWT token"""
        try:
            data = request.get_json()
            result = login_user(data)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/auth/me', methods=['GET'])
    @jwt_required()
    def api_get_current_user():
        """Get current authenticated user"""
        try:
            user_id = get_jwt_identity()
            result = get_current_user(user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    # ==================== WORKSPACE ROUTES ====================

    @app.route('/api/workspaces', methods=['POST'])
    @jwt_required()
    def api_create_workspace():
        """Create a new workspace"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            data['owner_id'] = user_id
            result = create_workspace(data)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/workspaces', methods=['GET'])
    @jwt_required()
    def api_get_workspaces():
        """Get all workspaces for current user"""
        try:
            user_id = get_jwt_identity()
            result = get_workspaces(user_id)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/workspaces/<int:workspace_id>', methods=['GET'])
    @jwt_required()
    def api_get_workspace(workspace_id):
        """Get specific workspace"""
        try:
            user_id = get_jwt_identity()
            result = get_workspace(workspace_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/workspaces/<int:workspace_id>', methods=['PUT'])
    @jwt_required()
    def api_update_workspace(workspace_id):
        """Update workspace"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            result = update_workspace(workspace_id, data, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/workspaces/<int:workspace_id>', methods=['DELETE'])
    @jwt_required()
    def api_delete_workspace(workspace_id):
        """Delete workspace"""
        try:
            user_id = get_jwt_identity()
            result = delete_workspace(workspace_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/workspaces/<int:workspace_id>/members', methods=['POST'])
    @jwt_required()
    def api_add_member(workspace_id):
        """Add member to workspace"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            result = add_member(workspace_id, data, user_id)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    # ==================== PROJECT ROUTES ====================

    @app.route('/api/projects', methods=['POST'])
    @jwt_required()
    def api_create_project():
        """Create a new project"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            data['created_by'] = user_id
            result = create_project(data)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/projects', methods=['GET'])
    @jwt_required()
    def api_get_projects():
        """Get projects with optional filters"""
        try:
            user_id = get_jwt_identity()
            workspace_id = request.args.get('workspace_id', type=int)
            status = request.args.get('status')
            filters = {
                'user_id': user_id,
                'workspace_id': workspace_id,
                'status': status
            }
            result = get_projects(filters)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/projects/<int:project_id>', methods=['GET'])
    @jwt_required()
    def api_get_project(project_id):
        """Get specific project"""
        try:
            user_id = get_jwt_identity()
            result = get_project(project_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/projects/<int:project_id>', methods=['PUT'])
    @jwt_required()
    def api_update_project(project_id):
        """Update project"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            result = update_project(project_id, data, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/projects/<int:project_id>', methods=['DELETE'])
    @jwt_required()
    def api_delete_project(project_id):
        """Delete project"""
        try:
            user_id = get_jwt_identity()
            result = delete_project(project_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    # ==================== TASK ROUTES ====================

    @app.route('/api/tasks', methods=['POST'])
    @jwt_required()
    def api_create_task():
        """Create a new task"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            data['created_by'] = user_id
            result = create_task(data)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/tasks', methods=['GET'])
    @jwt_required()
    def api_get_tasks():
        """Get tasks with optional filters"""
        try:
            user_id = get_jwt_identity()
            project_id = request.args.get('project_id', type=int)
            status = request.args.get('status')
            priority = request.args.get('priority')
            assigned_to = request.args.get('assigned_to', type=int)
            
            filters = {
                'user_id': user_id,
                'project_id': project_id,
                'status': status,
                'priority': priority,
                'assigned_to': assigned_to
            }
            result = get_tasks(filters)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/tasks/<int:task_id>', methods=['GET'])
    @jwt_required()
    def api_get_task(task_id):
        """Get specific task with details"""
        try:
            user_id = get_jwt_identity()
            result = get_task(task_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
    @jwt_required()
    def api_update_task(task_id):
        """Update task"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            result = update_task(task_id, data, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    @jwt_required()
    def api_delete_task(task_id):
        """Delete task"""
        try:
            user_id = get_jwt_identity()
            result = delete_task(task_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/tasks/<int:task_id>/assign', methods=['POST'])
    @jwt_required()
    def api_assign_user(task_id):
        """Assign user to task"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            result = assign_user(task_id, data, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
    @jwt_required()
    def api_update_status(task_id):
        """Update task status"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            result = update_status(task_id, data, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    # ==================== COMMENT ROUTES ====================

    @app.route('/api/comments', methods=['POST'])
    @jwt_required()
    def api_create_comment():
        """Create a new comment"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            data['user_id'] = user_id
            result = create_comment(data)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/tasks/<int:task_id>/comments', methods=['GET'])
    @jwt_required()
    def api_get_comments(task_id):
        """Get comments for a task"""
        try:
            user_id = get_jwt_identity()
            result = get_comments(task_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/comments/<int:comment_id>', methods=['PUT'])
    @jwt_required()
    def api_update_comment(comment_id):
        """Update comment"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            result = update_comment(comment_id, data, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/comments/<int:comment_id>', methods=['DELETE'])
    @jwt_required()
    def api_delete_comment(comment_id):
        """Delete comment"""
        try:
            user_id = get_jwt_identity()
            result = delete_comment(comment_id, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    # ==================== DOCUMENT ROUTES ====================

    @app.route('/api/documents', methods=['POST'])
    @jwt_required()
    def api_create_document():
        """Create a new document"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            data['created_by'] = user_id
            result = create_document(data)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/documents', methods=['GET'])
    @jwt_required()
    def api_get_documents():
        """Get documents with optional filters"""
        try:
            user_id = get_jwt_identity()
            project_id = request.args.get('project_id', type=int)
            task_id = request.args.get('task_id', type=int)
            
            filters = {
                'user_id': user_id,
                'project_id': project_id,
                'task_id': task_id
            }
            result = get_documents(filters)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/documents/<int:document_id>', methods=['PUT'])
    @jwt_required()
    def api_update_document(document_id):
        """Update document"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            result = update_document(document_id, data, user_id)
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except PermissionError as e:
            return jsonify({'error': str(e)}), 403
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    # ==================== CHAT ROUTES ====================

    @app.route('/api/chat/messages', methods=['POST'])
    @jwt_required()
    def api_send_message():
        """Send a chat message"""
        try:
            data = request.get_json()
            user_id = get_jwt_identity()
            data['user_id'] = user_id
            result = send_message(data)
            return jsonify(result), 201
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/chat/messages', methods=['GET'])
    @jwt_required()
    def api_get_messages():
        """Get chat messages with optional filters"""
        try:
            user_id = get_jwt_identity()
            project_id = request.args.get('project_id', type=int)
            task_id = request.args.get('task_id', type=int)
            limit = request.args.get('limit', type=int, default=50)
            
            filters = {
                'user_id': user_id,
                'project_id': project_id,
                'task_id': task_id,
                'limit': limit
            }
            result = get_messages(filters)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': 'Internal server error'}), 500

    # ==================== HEALTH CHECK ====================

    @app.route('/api/health', methods=['GET'])
    def api_health():
        """Health check endpoint"""
        return jsonify({'status': 'ok', 'message': 'TaskFlowAI API is running'}), 200

    return app
