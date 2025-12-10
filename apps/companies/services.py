from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from typing import List, Optional

from apps.companies.models import Company
from apps.companies.schemas import CompanyCreate, CompanyUpdate
from apps.auth.models import User


class CompanyService:
    @staticmethod
    def create_company(db: Session, company: CompanyCreate) -> Company:
        """Cria uma nova company e associa a um usuário"""
        # Verifica se o usuário existe
        user = db.query(User).filter(User.id == company.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Cria a company
        db_company = Company(
            name=company.name,
            description=company.description
        )
        db.add(db_company)
        db.flush()  # Para obter o ID
        
        # Associa o usuário à company
        db_company.users.append(user)
        db.commit()
        db.refresh(db_company)
        return db_company
    
    @staticmethod
    def get_company_by_id(db: Session, company_id: int, load_users: bool = False) -> Optional[Company]:
        """Obtém company por ID"""
        query = db.query(Company).filter(Company.id == company_id)
        if load_users:
            query = query.options(joinedload(Company.users))
        return query.first()
    
    @staticmethod
    def get_user_companies(db: Session, user_id: int) -> List[Company]:
        """Lista todas as companies de um usuário"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        return user.companies
    
    @staticmethod
    def is_user_member(db: Session, company_id: int, user_id: int) -> bool:
        """Verifica se um usuário é membro de uma company"""
        company = CompanyService.get_company_by_id(db, company_id)
        if not company:
            return False
        return any(user.id == user_id for user in company.users)
    
    @staticmethod
    def update_company(db: Session, company_id: int, company_update: CompanyUpdate) -> Company:
        """Atualiza uma company"""
        db_company = db.query(Company).filter(Company.id == company_id).first()
        if not db_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        update_data = company_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_company, key, value)
        
        db.commit()
        db.refresh(db_company)
        return db_company
    
    @staticmethod
    def add_user_to_company(db: Session, company_id: int, user_id: int) -> Company:
        """Adiciona um usuário a uma company"""
        company = CompanyService.get_company_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verifica se já é membro
        if CompanyService.is_user_member(db, company_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this company"
            )
        
        company.users.append(user)
        db.commit()
        db.refresh(company)
        # Força o carregamento dos usuários
        _ = company.users
        return company
    
    @staticmethod
    def remove_user_from_company(db: Session, company_id: int, user_id: int) -> Company:
        """Remove um usuário de uma company"""
        company = CompanyService.get_company_by_id(db, company_id)
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verifica se é membro
        if not CompanyService.is_user_member(db, company_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a member of this company"
            )
        
        company.users.remove(user)
        db.commit()
        db.refresh(company)
        # Força o carregamento dos usuários
        _ = company.users
        return company

