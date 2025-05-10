from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from stripe.error import StripeError

from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.services.payment_service import create_checkout_session, handle_webhook
from app.core.config import settings

# router = APIRouter(prefix="/payments", tags=["payments"])
router = APIRouter()

@router.post("/subscribe")
async def create_subscription(
        request: Request,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        session_url = create_checkout_session(current_user.id)
        return RedirectResponse(url=session_url)
    except StripeError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        return handle_webhook(payload, sig_header)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))