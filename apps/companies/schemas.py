from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from apps.auth.schemas import UserResponse


class CompanyBase(BaseModel):
    name: str
    description: Optional[str] = None


class CompanyCreate(CompanyBase):
    user_id: int  # ID do usuário que será associado à company


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompanyAddUser(BaseModel):
    user_id: int


class CompanyWithUsersResponse(CompanyResponse):
    """Company response com lista de usuários"""
    users: List[UserResponse]

    class Config:
        from_attributes = True

