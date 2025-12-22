import stripe
from flask import request, jsonify
import os

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class StripePayment:
    """Gerenciamento de pagamentos com Stripe"""
    
    @staticmethod
    def create_customer(email, name):
        """Criar cliente no Stripe"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name
            )
            return customer
        except Exception as e:
            print(f"Erro ao criar cliente: {e}")
            return None
    
    @staticmethod
    def create_subscription(customer_id, price_id):
        """Criar assinatura"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price_id}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent'],
                trial_period_days=14
            )
            return subscription
        except Exception as e:
            print(f"Erro ao criar assinatura: {e}")
            return None
    
    @staticmethod
    def cancel_subscription(subscription_id):
        """Cancelar assinatura"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return subscription
        except Exception as e:
            print(f"Erro ao cancelar assinatura: {e}")
            return None
    
    @staticmethod
    def create_checkout_session(price_id, success_url, cancel_url, customer_email=None):
        """Criar sessão de checkout"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=customer_email,
                subscription_data={
                    'trial_period_days': 14
                }
            )
            return session
        except Exception as e:
            print(f"Erro ao criar sessão de checkout: {e}")
            return None
    
    @staticmethod
    def construct_webhook_event(payload, sig_header, webhook_secret):
        """Construir evento do webhook"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except Exception as e:
            print(f"Erro no webhook: {e}")
            return None
    
    @staticmethod
    def get_subscription(subscription_id):
        """Obter detalhes da assinatura"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return subscription
        except Exception as e:
            print(f"Erro ao buscar assinatura: {e}")
            return None
    
    @staticmethod
    def create_portal_session(customer_id, return_url):
        """Criar sessão do portal do cliente"""
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=return_url,
            )
            return session
        except Exception as e:
            print(f"Erro ao criar portal: {e}")
            return None

# Preços de exemplo (substitua pelos seus IDs do Stripe)
STRIPE_PRICES = {
    'pro': {
        'monthly': 'price_pro_monthly',
        'annual': 'price_pro_annual'
    },
    'business': {
        'monthly': 'price_business_monthly',
        'annual': 'price_business_annual'
    }
}
