"""
Financial models for TaskFlowAI - Stripe integration
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from backend.database import db
import enum


class IntervalEnum(enum.Enum):
    """Subscription interval types"""
    month = "month"
    year = "year"


class SubscriptionStatusEnum(enum.Enum):
    """Subscription status types"""
    active = "active"
    canceled = "canceled"
    past_due = "past_due"
    trialing = "trialing"
    incomplete = "incomplete"
    incomplete_expired = "incomplete_expired"
    unpaid = "unpaid"


class PaymentStatusEnum(enum.Enum):
    """Payment status types"""
    succeeded = "succeeded"
    failed = "failed"
    pending = "pending"
    processing = "processing"
    canceled = "canceled"
    requires_action = "requires_action"


class Plan(db.Model):
    """Subscription plan model"""
    __tablename__ = 'plans'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    interval = Column(Enum(IntervalEnum), default=IntervalEnum.month, nullable=False)
    stripe_price_id = Column(String(100), unique=True)
    features = Column(JSON, default=list)
    is_active = Column(Boolean, default=True, nullable=False)
    max_workspaces = Column(Integer, default=1)
    max_projects = Column(Integer, default=5)
    max_users = Column(Integer, default=1)
    max_storage_gb = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    subscriptions = relationship('Subscription', back_populates='plan', lazy='dynamic')

    def __repr__(self):
        return f'<Plan {self.name} - {self.price} {self.currency}/{self.interval.value}>'

    def to_dict(self):
        """Convert plan to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.0,
            'currency': self.currency,
            'interval': self.interval.value if isinstance(self.interval, IntervalEnum) else self.interval,
            'stripe_price_id': self.stripe_price_id,
            'features': self.features or [],
            'is_active': self.is_active,
            'max_workspaces': self.max_workspaces,
            'max_projects': self.max_projects,
            'max_users': self.max_users,
            'max_storage_gb': self.max_storage_gb,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Subscription(db.Model):
    """User subscription model"""
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    plan_id = Column(Integer, ForeignKey('plans.id', ondelete='SET NULL'))
    stripe_subscription_id = Column(String(100), unique=True)
    stripe_customer_id = Column(String(100))
    status = Column(Enum(SubscriptionStatusEnum), default=SubscriptionStatusEnum.active, nullable=False)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='subscriptions')
    plan = relationship('Plan', back_populates='subscriptions')
    payments = relationship('Payment', back_populates='subscription', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Subscription {self.id} - User {self.user_id} - {self.status.value}>'

    def to_dict(self, include_plan=True, include_user=False):
        """Convert subscription to dictionary"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'stripe_subscription_id': self.stripe_subscription_id,
            'stripe_customer_id': self.stripe_customer_id,
            'status': self.status.value if isinstance(self.status, SubscriptionStatusEnum) else self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'cancel_at_period_end': self.cancel_at_period_end,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        if include_plan and self.plan:
            result['plan'] = self.plan.to_dict()

        if include_user and self.user:
            result['user'] = {
                'id': self.user.id,
                'email': self.user.email,
                'name': getattr(self.user, 'name', None)
            }

        return result

    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == SubscriptionStatusEnum.active and (
            not self.current_period_end or self.current_period_end > datetime.utcnow()
        )

    def days_until_renewal(self):
        """Calculate days until next renewal"""
        if not self.current_period_end:
            return None
        delta = self.current_period_end - datetime.utcnow()
        return max(0, delta.days)


class Payment(db.Model):
    """Payment transaction model"""
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    subscription_id = Column(Integer, ForeignKey('subscriptions.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    status = Column(Enum(PaymentStatusEnum), default=PaymentStatusEnum.pending, nullable=False)
    stripe_payment_intent_id = Column(String(100), unique=True)
    payment_method = Column(String(50))
    error_message = Column(String(500))
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    subscription = relationship('Subscription', back_populates='payments')

    def __repr__(self):
        return f'<Payment {self.id} - {self.amount} {self.currency} - {self.status.value}>'

    def to_dict(self, include_subscription=False):
        """Convert payment to dictionary"""
        result = {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'currency': self.currency,
            'status': self.status.value if isinstance(self.status, PaymentStatusEnum) else self.status,
            'stripe_payment_intent_id': self.stripe_payment_intent_id,
            'payment_method': self.payment_method,
            'error_message': self.error_message,
            'metadata': self.metadata or {},
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

        if include_subscription and self.subscription:
            result['subscription'] = self.subscription.to_dict(include_plan=True, include_user=False)

        return result

    def is_successful(self):
        """Check if payment was successful"""
        return self.status == PaymentStatusEnum.succeeded
