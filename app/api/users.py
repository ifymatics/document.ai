from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.config import settings

from app.controllers.user import get_user_by_email, update_user_premium_status
from app.core.security import verify_password
from app.db.database import get_db
from app.core.auth import get_current_user, create_access_token
from app.schemas.user import UserCreate, UserInDBBase, Token
from app.models.user import User
from app.services.payment_service import create_stripe_customer

router = APIRouter()


@router.post("/", response_model=UserInDBBase)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db, user=user)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/start_trial", response_model=dict)
async def start_trial(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    if current_user.trial_expires is not None:
        raise HTTPException(
            status_code=400,
            detail="Trial already used"
        )

    trial_end = datetime.now() + timedelta(days=7)
    update_user_premium_status(
        db,
        user_id=current_user.id,
        is_premium=True,
        trial_expires=trial_end
    )

    return {
        "status": "success",
        "trial_expires": trial_end.isoformat(),
        "message": "7-day trial activated"
    }