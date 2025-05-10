import stripe
from datetime import datetime
from fastapi import HTTPException
from app.core.config import settings
from app.controllers.user import get_user, get_user_by_stripe_id, update_user_premium_status
from app.db.database import get_db

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_customer(email: str):
    return stripe.Customer.create(email=email)


def create_checkout_session(user_id: int):
    db = next(get_db())
    try:
        user = get_user(db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': settings.STRIPE_PREMIUM_PRICE_ID,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{settings.FRONTEND_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.FRONTEND_URL}/payment/cancel",
        )

        return session.url
    finally:
        db.close()


def handle_webhook(payload: bytes, sig_header: str):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)

    # Handle subscription events
    elif event['type'] in [
        'customer.subscription.created',
        'customer.subscription.updated'
    ]:
        subscription = event['data']['object']
        handle_subscription_updated(subscription)

    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)

    return {"status": "success"}


def handle_checkout_session(session):
    db = next(get_db())
    try:
        customer_id = session['customer']
        user = get_user_by_stripe_id(db, customer_id)
        if user:
            update_user_premium_status(
                db,
                user_id=user.id,
                is_premium=True,
                trial_expires=None
            )
    finally:
        db.close()


def handle_subscription_updated(subscription):
    db = next(get_db())
    try:
        customer_id = subscription['customer']
        user = get_user_by_stripe_id(db, customer_id)
        if user:
            update_user_premium_status(
                db,
                user_id=user.id,
                is_premium=True,
                trial_expires=None
            )
    finally:
        db.close()


def handle_subscription_deleted(subscription):
    db = next(get_db())
    try:
        customer_id = subscription['customer']
        user = get_user_by_stripe_id(db, customer_id)
        if user:
            update_user_premium_status(
                db,
                user_id=user.id,
                is_premium=False
            )
    finally:
        db.close()