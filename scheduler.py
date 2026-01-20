from flask_apscheduler import APScheduler
from flask import current_app, render_template, url_for
from datetime import datetime, date
from models import db, User, System, DailyLog, Notification, MicroAction
from threading import Thread
import time

scheduler = APScheduler()

def init_scheduler(app):
    """Inicializa o scheduler com o app"""
    # Configurar APScheduler para usar timezone UTC ou o do servidor
    scheduler.init_app(app)
    scheduler.start()
    
    # Adicionar Jobs
    # OBS: Usando id para evitar duplicatas
    
    # 1. Briefing Matinal (07:00 Brasil / 10:00 UTC?) - Ajustar conforme server time
    # Vamos assumir server time UTC. 7h Brasil = 10h UTC.
    scheduler.add_job(id='morning_briefing', func=send_morning_briefing, trigger='cron', hour=10, minute=0, replace_existing=True)
    
    # 2. Salva Streak (20:00 Brasil = 23:00 UTC)
    scheduler.add_job(id='streak_saver', func=send_streak_saver, trigger='cron', hour=23, minute=0, replace_existing=True)
    
    print("Scheduler Inicializado: Jobs Morning Briefing & Streak Saver agendados.")

def send_morning_briefing():
    """Envia email com os rituais do dia para todos os usuários ativos"""
    with scheduler.app.app_context():
        print("Executando Job: Morning Briefing...")
        users = User.query.all() # Em prod, paginar se tiver muitos users
        today = datetime.utcnow().date()
        weekday = today.strftime('%a').lower() # mon, tue, etc (English locale?) 
        # Cuidado com locale. 
        # Melhor: weekday int . 0=Mon, 6=Sun
        weekday_idx = today.weekday() 
        weekdays_map = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
        today_slug = weekdays_map[weekday_idx]
        
        from app import send_email # Import local para evitar circular, ou mover send_email para utils
        
        for user in users:
            # Encontrar rituais de hoje
            # Simplificação: Pega todos e filtra por frequência em python
            systems = System.query.filter_by(goal_id=user.goals[0].id).all() if user.goals else [] 
            # (Lógica acima é frágil se user tiver >1 goal, melhor query systems direto via join)
            # Mas User não tem relação direta com Systems? Tem via Goals.
            
            # Melhor: iterar goals -> systems
            todays_systems = []
            if user.goals:
                for goal in user.goals:
                    for system in goal.systems:
                        if system.frequency == 'daily' or today_slug in system.frequency:
                            todays_systems.append(system)
            
            if todays_systems:
                # Criar Notificação In-App
                notif = Notification(
                    title="Briefing Matinal",
                    content=f"Você tem {len(todays_systems)} rituais hoje. Foco!",
                    type="briefing",
                    user_id=user.id,
                    link="/dashboard"
                )
                db.session.add(notif)
                
                # Enviar Email
                html_body = f"""
                <h3>Bom dia, {user.username}! ☀️</h3>
                <p>O sucesso é construído hoje. Aqui está seu foco:</p>
                <ul>
                """
                for sys in todays_systems:
                    html_body += f"<li><strong>{sys.title}</strong> ({sys.time_of_day or 'Qualquer horário'})</li>"
                
                html_body += """
                </ul>
                <p><a href="https://ritualos.com.br/dashboard">Acessar RitualOS</a></p>
                """
                try:
                    send_email(user.email, f"Briefing Matinal: {len(todays_systems)} Rituais", html_body)
                except Exception as e:
                    print(f"Erro email {user.username}: {e}")
                    
        db.session.commit()

def send_streak_saver():
    """Verifica quem não fez NADA hoje e manda alerta"""
    with scheduler.app.app_context():
        print("Executando Job: Streak Saver...")
        users = User.query.all()
        today = datetime.utcnow().date()
        from app import send_email
        
        for user in users:
            # Checar DailyLog de hoje
            log = DailyLog.query.filter_by(user_id=user.id, date=today).first()
            
            has_activity = False
            if log and log.completed_actions:
                has_activity = True
                
            if not has_activity:
                # Alerta Vermelho!
                notif = Notification(
                    title="🔥 Perigo de Quebrar o Streak!",
                    content="Você não concluiu nenhum ritual hoje. Faça 5 minutos para salvar sua corrente.",
                    type="alert",
                    user_id=user.id,
                    link="/dashboard"
                )
                db.session.add(notif)
                
                html_body = f"""
                <h3>🚨 Alerta de Protocolo: NÃO QUEBRE A CORRENTE</h3>
                <p>{user.username}, o dia está acabando e não registramos atividades.</p>
                <p>Consistência > Intensidade.</p>
                <p>Faça algo pequeno. Agora.</p>
                <p><a href="https://ritualos.com.br/dashboard">✅ Salvar Meu Streak</a></p>
                """
                try:
                    send_email(user.email, "🚨 Risco de Perder Streak", html_body)
                except:
                    pass
        
        db.session.commit()
