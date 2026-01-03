import openai
import json
from typing import List, Dict, Any, Optional

class AIService:
    """Serviço de integração com IA (OpenAI)"""
    
    def __init__(self, api_key: str = None):
        self.api_key = None
        self.set_api_key(api_key)

    def set_api_key(self, api_key: Optional[str]):
        """Atualiza a chave da API em tempo real."""
        self.api_key = api_key
        if api_key:
            openai.api_key = api_key
        else:
            openai.api_key = None
    
    def generate_tasks_from_description(self, description: str) -> List[Dict[str, Any]]:
        """
        Gera tarefas automaticamente a partir de uma descrição
        """
        if not self.api_key:
            return self._generate_tasks_fallback(description)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um assistente especializado em gerenciamento de projetos.
                        Sua função é quebrar descrições de projetos em tarefas específicas e acionáveis.
                        Retorne as tarefas no formato JSON: [{"title": "...", "description": "...", "priority": "low|medium|high|urgent"}]"""
                    },
                    {
                        "role": "user",
                        "content": f"Crie tarefas específicas para o seguinte projeto/objetivo:\n\n{description}"
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            tasks = json.loads(content)
            return tasks
            
        except Exception as e:
            print(f"Erro ao gerar tarefas com IA: {e}")
            return self._generate_tasks_fallback(description)
    
    def _generate_tasks_fallback(self, description: str) -> List[Dict[str, Any]]:
        """
        Fallback simples quando a API não está disponível
        """
        return [
            {
                "title": f"Tarefa gerada: {description[:50]}...",
                "description": description,
                "priority": "medium"
            }
        ]
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        Resume um texto longo
        """
        if not self.api_key:
            return text[:max_length] + "..."
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um assistente que resume textos de forma concisa e clara."
                    },
                    {
                        "role": "user",
                        "content": f"Resuma o seguinte texto em no máximo {max_length} caracteres:\n\n{text}"
                    }
                ],
                temperature=0.5,
                max_tokens=100
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erro ao resumir texto: {e}")
            return text[:max_length] + "..."
    
    def analyze_project_structure(self, project_description: str) -> Dict[str, Any]:
        """
        Analisa uma descrição de projeto e sugere estrutura completa
        """
        if not self.api_key:
            return self._analyze_project_fallback(project_description)
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um especialista em estruturação de projetos.
                        Analise a descrição e retorne uma estrutura JSON com:
                        {
                            "project_name": "...",
                            "description": "...",
                            "spaces": [{"name": "...", "description": "..."}],
                            "lists": [{"name": "...", "description": "..."}],
                            "tasks": [{"title": "...", "description": "...", "priority": "..."}]
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"Estruture o seguinte projeto:\n\n{project_description}"
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            structure = json.loads(content)
            return structure
            
        except Exception as e:
            print(f"Erro ao analisar estrutura do projeto: {e}")
            return self._analyze_project_fallback(project_description)
    
    def _analyze_project_fallback(self, description: str) -> Dict[str, Any]:
        """
        Fallback para análise de projeto
        """
        return {
            "project_name": "Novo Projeto",
            "description": description,
            "spaces": [],
            "lists": [
                {"name": "A Fazer", "description": "Tarefas pendentes"},
                {"name": "Em Progresso", "description": "Tarefas em andamento"},
                {"name": "Concluído", "description": "Tarefas finalizadas"}
            ],
            "tasks": []
        }
    
    def suggest_deadline(self, task_description: str, complexity: str = "medium") -> str:
        """
        Sugere um prazo baseado na descrição da tarefa
        """
        complexity_days = {
            "low": 2,
            "medium": 5,
            "high": 10,
            "urgent": 1
        }
        
        from datetime import datetime, timedelta
        suggested_date = datetime.now() + timedelta(days=complexity_days.get(complexity, 5))
        return suggested_date.strftime("%Y-%m-%d")
    
    def extract_action_items(self, meeting_notes: str) -> List[Dict[str, Any]]:
        """
        Extrai itens de ação de notas de reunião
        """
        if not self.api_key:
            return []
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Você extrai itens de ação de notas de reunião.
                        Retorne JSON: [{"action": "...", "responsible": "...", "deadline": "..."}]"""
                    },
                    {
                        "role": "user",
                        "content": f"Extraia os itens de ação destas notas:\n\n{meeting_notes}"
                    }
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            items = json.loads(content)
            return items
            
        except Exception as e:
            print(f"Erro ao extrair itens de ação: {e}")
            return []
    
    def analyze_csv_data(self, csv_content: str) -> Dict[str, Any]:
        """
        Analisa dados CSV e gera insights
        """
        if not self.api_key:
            return {"insights": [], "summary": "Análise não disponível"}
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Você analisa dados CSV e fornece insights úteis em JSON."
                    },
                    {
                        "role": "user",
                        "content": f"Analise estes dados CSV e forneça insights:\n\n{csv_content[:2000]}"
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            analysis = json.loads(content)
            return analysis
            
        except Exception as e:
            print(f"Erro ao analisar CSV: {e}")
            return {"insights": [], "summary": "Erro na análise"}
    
    def suggest_automation(self, workflow_description: str) -> Dict[str, Any]:
        """
        Sugere automações baseadas na descrição do fluxo de trabalho
        """
        if not self.api_key:
            return {"automations": []}
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Você sugere automações para fluxos de trabalho.
                        Retorne JSON: {"automations": [{"trigger": "...", "action": "...", "description": "..."}]}"""
                    },
                    {
                        "role": "user",
                        "content": f"Sugira automações para este fluxo:\n\n{workflow_description}"
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            suggestions = json.loads(content)
            return suggestions
            
        except Exception as e:
            print(f"Erro ao sugerir automações: {e}")
            return {"automations": []}
    
    def answer_question(self, question: str, context: str = "") -> str:
        """
        Responde perguntas sobre o workspace
        """
        if not self.api_key:
            return "Serviço de IA não está configurado. Por favor, configure a chave da API OpenAI."
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Você é um assistente útil que responde perguntas sobre gestão de projetos e tarefas."
                }
            ]
            
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Contexto: {context}"
                })
            
            messages.append({
                "role": "user",
                "content": question
            })
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Erro ao responder pergunta: {e}")
    def generate_ritual_system(self, goal: str, pillar: str = "general") -> Dict[str, Any]:
        """
        Gera um Sistema (Ritual) a partir de uma Meta, seguindo a filosofia Kaizen.
        Retorna estrutura com versão Ideal e versão Pior Dia.
        """
        if not self.api_key:
            return self._generate_ritual_fallback(goal)
            
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini", # Usar modelo inteligente
                messages=[
                    {
                        "role": "system",
                        "content": """Você é um Arquiteto de Hábitos especialista em Kaizen e Antifragilidade.
                        Sua missão: Converter Metas abstratas em Sistemas repetíveis.
                        
                        REGRAS:
                        1. FILOSOFIA KAIZEN: O passo inicial deve ser ridiculamente pequeno.
                        2. MODOS DUPLOS: Crie duas versões da rotina:
                           - MODO IDEAL: O que fazer num dia normal (desafiador mas possível).
                           - MODO PIOR DIA: O mínimo absoluto para não quebrar a corrente (ex: 1 flexão, ler 1 frase).
                        
                        SAÍDA JSON OBRIGATÓRIA:
                        {
                            "system_title": "Nome criativo do ritual (ex: Protocolo X)",
                            "description": "Explicação breve do porquê funciona",
                            "frequency": "daily",
                            "time_of_day": "morning",
                            "micro_actions": [
                                {
                                    "action_ideal": "Ação completa (ex: Correr 5km)",
                                    "action_bad_day": "Ação de sobrevivência (ex: Vestir o tênis e andar 5min)",
                                    "duration_minutes": 30
                                }
                            ]
                        }"""
                    },
                    {
                        "role": "user",
                        "content": f"Crie um sistema para a meta: '{goal}'. Pilar: {pillar}."
                    }
                ],
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Erro ao gerar ritual: {e}")
            return self._generate_ritual_fallback(goal)

    def _generate_ritual_fallback(self, goal: str) -> Dict[str, Any]:
        return {
            "system_title": f"Ritual para {goal}",
            "description": "Sistema gerado automaticamente (modo offline).",
            "frequency": "daily",
            "time_of_day": "morning",
            "micro_actions": [
                {
                    "action_ideal": f"Trabalhar 20min em {goal}",
                    "action_bad_day": f"Pensar sobre {goal} por 1min",
                    "duration_minutes": 20
                }
            ]
        }

