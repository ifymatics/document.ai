from typing import Optional

from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.security import get_password_hash,  verify_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
# from app.core.auth import verify_password
#from app.services.payment_service import create_stripe_customer


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_update.model_dump(exclude_unset=True)

    if 'new_password' in update_data:
        if not verify_password(update_data['current_password'], db_user.hashed_password):
            raise ValueError("Current password is incorrect")
        db_user.hashed_password = get_password_hash(update_data['new_password'])

    for field, value in update_data.items():
        if field not in ['current_password', 'new_password'] and hasattr(db_user, field):
            setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def activate_premium(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    db_user.is_premium = True
    db_user.trial_expires = None  # End trial if active
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_stripe_id(db: Session, stripe_id: str):
    return db.query(User).filter(User.stripe_customer_id == stripe_id).first()

def start_trial(db: Session, user_id: int, days: int = 7):
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    if db_user.trial_expires is not None:
        raise ValueError("Trial already used")

    db_user.is_premium = True
    db_user.trial_expires = datetime.utcnow() + timedelta(days=days)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_premium_status(
        db: Session,
        user_id: int,
        is_premium: bool,
        trial_expires: Optional[datetime] = None
):
    db_user = get_user(db, user_id)
    if db_user:
        db_user.is_premium = is_premium
        if trial_expires is not None:
            db_user.trial_expires = trial_expires
        db.commit()
        db.refresh(db_user)
    return db_user


