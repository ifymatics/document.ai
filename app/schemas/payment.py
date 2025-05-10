from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class PaymentBase(BaseModel):
    user_id: int
    amount: float
    currency: str = "USD"
    status: str

class PaymentCreate(PaymentBase):
    stripe_session_id: str
    stripe_subscription_id: Optional[str] = None

class PaymentOut(PaymentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True