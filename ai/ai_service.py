from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import openai
import os
import json

openai.api_key = os.environ.get('OPENAI_API_KEY', '')

def create_ai_routes(app):
    """Registrar rotas de IA"""
    
    @app.route('/api/ai/generate-tasks', methods=['POST'])
    @jwt_required()
    def generate_tasks():
        """Gerar tarefas automaticamente a partir de descrição"""
        data = request.get_json()
        description = data.get('description')
        
        if not description:
            return jsonify({'error': 'Description required'}), 400
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você é um assistente que ajuda a criar tarefas estruturadas a partir de descrições. Retorne um JSON com array de tarefas, cada uma com title, description, priority (low/normal/high/urgent), e estimated_time em minutos."},
                    {"role": "user", "content": f"Crie tarefas para: {description}"}
                ],
                temperature=0.7
            )
            
            tasks = json.loads(response.choices[0].message.content)
            return jsonify({'tasks': tasks})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ai/summarize', methods=['POST'])
    @jwt_required()
    def summarize_content():
        """Resumir conteúdo (documentos, conversas, etc)"""
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({'error': 'Content required'}), 400
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Resuma o seguinte conteúdo de forma concisa e objetiva."},
                    {"role": "user", "content": content}
                ],
                temperature=0.5
            )
            
            summary = response.choices[0].message.content
            return jsonify({'summary': summary})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ai/structure-project', methods=['POST'])
    @jwt_required()
    def structure_project():
        """Estruturar projeto automaticamente"""
        data = request.get_json()
        project_description = data.get('description')
        
        if not project_description:
            return jsonify({'error': 'Project description required'}), 400
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Você estrutura projetos criando listas e tarefas organizadas. Retorne JSON com: lists (array com name), e tasks (array com title, description, list_name, priority)."},
                    {"role": "user", "content": f"Estruture este projeto: {project_description}"}
                ],
                temperature=0.7
            )
            
            structure = json.loads(response.choices[0].message.content)
            return jsonify(structure)
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ai/analyze-data', methods=['POST'])
    @jwt_required()
    def analyze_data():
        """Analisar dados de CSV/Excel e gerar insights"""
        data = request.get_json()
        csv_data = data.get('data')
        
        if not csv_data:
            return jsonify({'error': 'Data required'}), 400
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Analise os dados fornecidos e gere insights relevantes, tendências e sugestões de ação."},
                    {"role": "user", "content": f"Dados:\n{csv_data}"}
                ],
                temperature=0.6
            )
            
            insights = response.choices[0].message.content
            return jsonify({'insights': insights})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ai/suggest-automation', methods=['POST'])
    @jwt_required()
    def suggest_automation():
        """Sugerir automações para o workspace"""
        data = request.get_json()
        workflow_description = data.get('workflow')
        
        if not workflow_description:
            return jsonify({'error': 'Workflow description required'}), 400
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Sugira automações práticas para otimizar o fluxo de trabalho descrito. Retorne JSON com array de automações, cada uma com: trigger, action, description."},
                    {"role": "user", "content": f"Fluxo de trabalho: {workflow_description}"}
                ],
                temperature=0.7
            )
            
            automations = json.loads(response.choices[0].message.content)
            return jsonify({'automations': automations})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/ai/assistant', methods=['POST'])
    @jwt_required()
    def ai_assistant():
        """Assistente geral de IA para responder perguntas"""
        data = request.get_json()
        question = data.get('question')
        context = data.get('context', '')
        
        if not question:
            return jsonify({'error': 'Question required'}), 400
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"Você é um assistente inteligente do TaskFlowAI que ajuda usuários com gerenciamento de projetos e tarefas. Contexto: {context}"},
                    {"role": "user", "content": question}
                ],
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            return jsonify({'answer': answer})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
