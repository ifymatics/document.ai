from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.auth import get_current_user, is_super_admin
from app.schemas.user import UserAdminView
from app.models.user import User
from app.models.payment import Payment
from app.models.document import Document
from app.schemas.payment import PaymentOut

router = APIRouter()


@router.get("/users", response_model=List[UserAdminView])
async def get_all_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(is_super_admin)
):
    """Get all users (admin only)"""
    return db.query(User).offset(skip).limit(limit).all()


@router.post("/users/{user_id}/block")
async def block_user(
        user_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(is_super_admin)
):
    """Block a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
    return {"status": "success", "blocked": True}


@router.get("/payments", response_model=List[PaymentOut])
async def get_all_payments(
        db: Session = Depends(get_db),
        current_user: User = Depends(is_super_admin)
):
    """Get all payment records (admin only)"""
    return db.query(Payment).all()

from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())