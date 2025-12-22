import stripe
import os

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_...')

def create_customer(email, name):
    """Criar customer no Stripe"""
    customer = stripe.Customer.create(
        email=email,
        name=name
    )
    return customer.id

def create_checkout_session(customer_id, price_id, success_url, cancel_url):
    """Criar sessão de checkout"""
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session

def cancel_subscription(subscription_id):
    """Cancelar assinatura"""
    subscription = stripe.Subscription.modify(
        subscription_id,
        cancel_at_period_end=True
    )
    return subscription

def create_payment_intent(amount, currency, customer_id):
    """Criar intenção de pagamento"""
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
        customer=customer_id
    )
    return intent
