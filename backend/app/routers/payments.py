"""
Payments Router (Stripe integration)
POST /payments/create-checkout  - Create a Stripe Checkout session
POST /payments/webhook          - Handle Stripe webhook events
GET  /payments/subscription     - Get current subscription status
POST /payments/cancel           - Cancel subscription
POST /payments/validate-discount - Validate a discount code
"""

import logging
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..db_models import DiscountCode, Subscription, User, UserTier
from ..dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["payments"])

stripe.api_key = settings.stripe_secret_key


@router.post("/create-checkout")
async def create_checkout(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session for Pro upgrade."""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Payments not configured.")

    body = await request.json()
    discount_code = body.get("discount_code")

    # Validate discount code if provided
    stripe_coupon_id = None
    if discount_code:
        code_obj = (
            db.query(DiscountCode)
            .filter(DiscountCode.code == discount_code, DiscountCode.active == 1)
            .first()
        )
        if not code_obj:
            raise HTTPException(status_code=400, detail="Invalid discount code.")
        if code_obj.max_uses and code_obj.times_used >= code_obj.max_uses:
            raise HTTPException(status_code=400, detail="Discount code has been fully redeemed.")
        if code_obj.valid_until and code_obj.valid_until < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Discount code has expired.")

        try:
            coupon_params: dict = {"duration": "once"}
            if code_obj.percent_off:
                coupon_params["percent_off"] = code_obj.percent_off
            elif code_obj.amount_off:
                coupon_params["amount_off"] = int(code_obj.amount_off)
                coupon_params["currency"] = "usd"
            stripe_coupon = stripe.Coupon.create(**coupon_params)
            stripe_coupon_id = stripe_coupon.id
        except Exception as e:
            logger.error("Failed to create Stripe coupon: %s", e)

    # Ensure user has a Stripe customer ID
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email, name=user.display_name)
        user.stripe_customer_id = customer.id
        db.commit()

    session_params: dict = {
        "mode": "subscription",
        "customer": user.stripe_customer_id,
        "line_items": [{"price": settings.stripe_price_id_pro, "quantity": 1}],
        "success_url": body.get("success_url", "http://localhost:5173/?upgraded=1"),
        "cancel_url": body.get("cancel_url", "http://localhost:5173/"),
        "metadata": {"user_id": user.id},
    }
    if stripe_coupon_id:
        session_params["discounts"] = [{"coupon": stripe_coupon_id}]

    session = stripe.checkout.Session.create(**session_params)
    return {"checkout_url": session.url, "session_id": session.id}


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.stripe_webhook_secret
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid webhook signature.")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.tier = UserTier.PRO
                sub = Subscription(
                    user_id=user.id,
                    stripe_subscription_id=data.get("subscription"),
                    plan="pro",
                    status="active",
                )
                db.add(sub)
                db.commit()

    elif event_type == "invoice.payment_failed":
        sub_id = data.get("subscription")
        if sub_id:
            sub = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == sub_id
            ).first()
            if sub:
                sub.status = "past_due"
                db.commit()

    elif event_type == "customer.subscription.deleted":
        sub_id = data.get("id")
        if sub_id:
            sub = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == sub_id
            ).first()
            if sub:
                sub.status = "canceled"
                user = db.query(User).filter(User.id == sub.user_id).first()
                if user:
                    user.tier = UserTier.FREE
                db.commit()

    return {"received": True}


@router.get("/subscription")
async def get_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the user's current subscription status."""
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.status == "active")
        .first()
    )
    return {
        "tier": user.tier.value,
        "subscription": {
            "id": sub.id,
            "plan": sub.plan,
            "status": sub.status,
            "current_period_end": sub.current_period_end.isoformat() if sub.current_period_end else None,
        } if sub else None,
    }


@router.post("/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel the user's subscription at period end."""
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.status == "active")
        .first()
    )
    if not sub or not sub.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription found.")

    try:
        stripe.Subscription.modify(
            sub.stripe_subscription_id,
            cancel_at_period_end=True,
        )
        sub.status = "canceled"
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel: {e}")

    return {"success": True, "message": "Subscription will cancel at end of billing period."}


@router.post("/validate-discount")
async def validate_discount(
    request: Request,
    db: Session = Depends(get_db),
):
    """Validate a discount code without requiring authentication."""
    body = await request.json()
    code_str = body.get("code", "")

    code_obj = (
        db.query(DiscountCode)
        .filter(DiscountCode.code == code_str, DiscountCode.active == 1)
        .first()
    )
    if not code_obj:
        return {"valid": False, "message": "Invalid discount code."}
    if code_obj.max_uses and code_obj.times_used >= code_obj.max_uses:
        return {"valid": False, "message": "Discount code has been fully redeemed."}
    if code_obj.valid_until and code_obj.valid_until < datetime.now(timezone.utc):
        return {"valid": False, "message": "Discount code has expired."}

    return {
        "valid": True,
        "percent_off": code_obj.percent_off,
        "amount_off": code_obj.amount_off,
    }
