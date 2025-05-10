from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

    @field_validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('passwords do not match')
        return v

class UserUpdate(UserBase):
    current_password: Optional[str] = Field(None, min_length=8, max_length=100)
    new_password: Optional[str] = Field(None, min_length=8, max_length=100)

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_premium: bool
    trial_expires: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):

    has_premium_access: bool = False

    @field_validator('has_premium_access')
    def set_has_premium_access(cls, v, values):
        return values.get('is_premium', False) or (
            values.get('trial_expires') and values.get('trial_expires') > datetime.utcnow()
        )

class UserWithToken(User):
    access_token: str
    token_type: str = "bearer"

class UserPublic(UserInDBBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None



class UserAdminView(UserInDBBase):
    is_active: bool
    is_superadmin: bool
    is_premium: bool
    trial_expires: Optional[datetime]
    premium_since: Optional[datetime]
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True