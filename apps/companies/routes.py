from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from core.database import get_db
from core.security import get_current_active_user, require_role
from apps.auth.models import User, UserRole
from apps.companies.schemas import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyAddUser,
    CompanyWithUsersResponse
)
from apps.companies.services import CompanyService

router = APIRouter()


@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN))
):
    """Cria uma nova company e associa a um usuário (apenas admin)"""
    return CompanyService.create_company(db, company)


@router.get("/companies", response_model=List[CompanyResponse])
async def get_my_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista todas as companies do usuário atual"""
    companies = CompanyService.get_user_companies(db, current_user.id)
    return companies


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém uma company por ID (apenas se o usuário for membro)"""
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Verifica se o usuário é membro
    if not CompanyService.is_user_member(db, company_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this company"
        )
    
    return company


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Atualiza uma company (apenas se o usuário for membro)"""
    # Verifica se a company existe
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Verifica se o usuário é membro
    if not CompanyService.is_user_member(db, company_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this company"
        )
    
    return CompanyService.update_company(db, company_id, company_update)


@router.post("/companies/{company_id}/users", response_model=CompanyWithUsersResponse)
async def add_user_to_company(
    company_id: int,
    user_data: CompanyAddUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Adiciona um usuário a uma company (apenas se o usuário atual for membro)"""
    # Verifica se a company existe
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Verifica se o usuário atual é membro
    if not CompanyService.is_user_member(db, company_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this company"
        )
    
    company = CompanyService.add_user_to_company(db, company_id, user_data.user_id)
    # Força o carregamento dos usuários
    _ = company.users  # Acessa para forçar o carregamento
    return company


@router.delete("/companies/{company_id}/users/{user_id}", response_model=CompanyWithUsersResponse)
async def remove_user_from_company(
    company_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Remove um usuário de uma company (apenas se o usuário atual for membro)"""
    # Verifica se a company existe
    company = CompanyService.get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Verifica se o usuário atual é membro
    if not CompanyService.is_user_member(db, company_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this company"
        )
    
    company = CompanyService.remove_user_from_company(db, company_id, user_id)
    # Força o carregamento dos usuários
    _ = company.users  # Acessa para forçar o carregamento
    return company

