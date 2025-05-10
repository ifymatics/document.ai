from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
# from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# from app.core.auth import get_password_hash
from app.db.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_subscription_id = Column(String, unique=True, index=True)
    status = Column(String)  # active, past_due, canceled, etc.
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    user = relationship("User", back_populates="subscriptions")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    is_active = Column(Boolean, default=True)
    disabled = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    trial_expires = Column(DateTime)
    stripe_customer_id = Column(String, unique=True, index=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    

    # Relationships
    documents = relationship("Document", back_populates="user")

    payment_history = relationship("Payment", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    # payments = relationship("Payment", back_populates="user")
    
  
   
  


    # def get_full_name(self):
    #     return f"{self.first_name} {self.last_name}"

    # def is_trial_active(self):
    #     return self.trial_expires and self.trial_expires > datetime.utcnow()
    #
    # def has_premium_access(self):
    #     return self.is_premium or self.is_trial_active()
    #
    # def set_password(self, password: str):
    #     self.hashed_password = get_password_hash(password)

    # def verify_password(self, password: str) -> bool:
    #     from app.core.auth import verify_password
    #     return verify_password(password, self.hashed_password)
    
# Index('idx_user_payment', User.payments)
# Index('idx_user_resume', User.resumes)