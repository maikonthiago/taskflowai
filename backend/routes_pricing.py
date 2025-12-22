from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models_finance import Plan, Subscription, Payment
from backend.models import User
from backend.database import db
from backend.stripe_service import create_checkout_session, create_customer, cancel_subscription
from datetime import datetime

pricing_bp = Blueprint('pricing', __name__)

@pricing_bp.route('/plans', methods=['GET'])
def get_plans():
    """Get all active subscription plans"""
    plans = Plan.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in plans])

@pricing_bp.route('/plans/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    """Get specific plan details"""
    plan = Plan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404
    return jsonify(plan.to_dict())

@pricing_bp.route('/checkout', methods=['POST'])
@jwt_required()
def create_checkout():
    """Create Stripe checkout session"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    plan_id = data.get('plan_id')
    
    plan = Plan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Plan not found'}), 404
    
    try:
        # Criar customer no Stripe se não existir
        subscription = Subscription.query.filter_by(user_id=user.id).first()
        if not subscription or not subscription.stripe_customer_id:
            customer_id = create_customer(user.email, user.full_name)
        else:
            customer_id = subscription.stripe_customer_id
        
        # Criar sessão de checkout
        session = create_checkout_session(
            customer_id=customer_id,
            price_id=plan.stripe_price_id,
            success_url=data.get('success_url', 'http://localhost:5000/dashboard'),
            cancel_url=data.get('cancel_url', 'http://localhost:5000/pricing')
        )
        
        return jsonify({
            'checkout_url': session.url,
            'session_id': session.id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@pricing_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription():
    """Get current user subscription"""
    current_user_id = get_jwt_identity()
    subscription = Subscription.query.filter_by(user_id=current_user_id).first()
    
    if not subscription:
        return jsonify({'subscription': None, 'plan': None})
    
    return jsonify({
        'subscription': subscription.to_dict(),
        'plan': subscription.plan.to_dict() if subscription.plan else None
    })

@pricing_bp.route('/subscription/cancel', methods=['POST'])
@jwt_required()
def cancel_user_subscription():
    """Cancel user subscription"""
    current_user_id = get_jwt_identity()
    subscription = Subscription.query.filter_by(user_id=current_user_id).first()
    
    if not subscription:
        return jsonify({'error': 'No active subscription'}), 404
    
    try:
        # Cancelar no Stripe
        cancel_subscription(subscription.stripe_subscription_id)
        
        # Atualizar no banco
        subscription.status = 'canceled'
        subscription.cancel_at_period_end = True
        subscription.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Subscription canceled successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@pricing_bp.route('/payments', methods=['GET'])
@jwt_required()
def get_payments():
    """Get user payment history"""
    current_user_id = get_jwt_identity()
    subscription = Subscription.query.filter_by(user_id=current_user_id).first()
    
    if not subscription:
        return jsonify([])
    
    payments = Payment.query.filter_by(subscription_id=subscription.id).order_by(Payment.created_at.desc()).all()
    return jsonify([p.to_dict() for p in payments])

@pricing_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks"""
    # Este endpoint seria configurado no Stripe para receber eventos
    # Por segurança, deve verificar a assinatura do webhook
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        # Processar evento do Stripe
        # TODO: Implementar lógica completa de webhook
        return jsonify({'received': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400
