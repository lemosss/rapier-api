import pytest
from fastapi import HTTPException
from apps.companies.services import CompanyService
from apps.companies.schemas import CompanyCreate, CompanyUpdate
from apps.auth.services import UserService
from apps.auth.schemas import UserCreate
from apps.auth.models import UserRole


def test_create_company(db, test_user):
    """Testa criação de company"""
    company_data = CompanyCreate(
        name="Test Company",
        description="Test Description",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    
    assert company.id is not None
    assert company.name == "Test Company"
    assert company.description == "Test Description"
    assert len(company.users) == 1
    assert company.users[0].id == test_user.id


def test_create_company_user_not_found(db):
    """Testa criação de company com usuário inexistente"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=99999
    )
    with pytest.raises(HTTPException) as exc_info:
        CompanyService.create_company(db, company_data)
    assert exc_info.value.status_code == 404


def test_get_company_by_id(db, test_user):
    """Testa obtenção de company por ID"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=test_user.id
    )
    created_company = CompanyService.create_company(db, company_data)
    
    company = CompanyService.get_company_by_id(db, created_company.id)
    assert company is not None
    assert company.id == created_company.id
    assert company.name == "Test Company"


def test_get_company_by_id_not_found(db):
    """Testa obtenção de company inexistente"""
    company = CompanyService.get_company_by_id(db, 99999)
    assert company is None


def test_get_user_companies(db, test_user):
    """Testa listagem de companies de um usuário"""
    # Cria companies
    company1_data = CompanyCreate(name="Company 1", user_id=test_user.id)
    company2_data = CompanyCreate(name="Company 2", user_id=test_user.id)
    
    CompanyService.create_company(db, company1_data)
    CompanyService.create_company(db, company2_data)
    
    companies = CompanyService.get_user_companies(db, test_user.id)
    assert len(companies) == 2
    company_names = [c.name for c in companies]
    assert "Company 1" in company_names
    assert "Company 2" in company_names


def test_get_user_companies_empty(db, test_user):
    """Testa listagem de companies quando usuário não tem nenhuma"""
    companies = CompanyService.get_user_companies(db, test_user.id)
    assert len(companies) == 0


def test_get_user_companies_user_not_found(db):
    """Testa listagem de companies de usuário inexistente"""
    companies = CompanyService.get_user_companies(db, 99999)
    assert len(companies) == 0


def test_is_user_member(db, test_user):
    """Testa verificação de membro"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    
    assert CompanyService.is_user_member(db, company.id, test_user.id) is True


def test_is_user_member_false(db, test_user, test_admin):
    """Testa verificação de membro quando não é membro"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    
    assert CompanyService.is_user_member(db, company.id, test_admin.id) is False


def test_is_user_member_company_not_found(db, test_user):
    """Testa verificação de membro com company inexistente"""
    assert CompanyService.is_user_member(db, 99999, test_user.id) is False


def test_update_company(db, test_user):
    """Testa atualização de company"""
    company_data = CompanyCreate(
        name="Test Company",
        description="Old Description",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    
    company_update = CompanyUpdate(
        name="Updated Company",
        description="New Description"
    )
    updated_company = CompanyService.update_company(db, company.id, company_update)
    
    assert updated_company.name == "Updated Company"
    assert updated_company.description == "New Description"


def test_update_company_not_found(db):
    """Testa atualização de company inexistente"""
    company_update = CompanyUpdate(name="Updated Company")
    with pytest.raises(HTTPException) as exc_info:
        CompanyService.update_company(db, 99999, company_update)
    assert exc_info.value.status_code == 404


def test_add_user_to_company(db, test_user, test_admin):
    """Testa adicionar usuário a uma company"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    
    updated_company = CompanyService.add_user_to_company(db, company.id, test_admin.id)
    
    assert len(updated_company.users) == 2
    user_ids = [u.id for u in updated_company.users]
    assert test_user.id in user_ids
    assert test_admin.id in user_ids


def test_add_user_to_company_already_member(db, test_user):
    """Testa adicionar usuário que já é membro"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    
    with pytest.raises(HTTPException) as exc_info:
        CompanyService.add_user_to_company(db, company.id, test_user.id)
    assert exc_info.value.status_code == 400


def test_add_user_to_company_not_found(db, test_user):
    """Testa adicionar usuário a company inexistente"""
    with pytest.raises(HTTPException) as exc_info:
        CompanyService.add_user_to_company(db, 99999, test_user.id)
    assert exc_info.value.status_code == 404


def test_add_user_to_company_user_not_found(db, test_user):
    """Testa adicionar usuário inexistente a company"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    
    with pytest.raises(HTTPException) as exc_info:
        CompanyService.add_user_to_company(db, company.id, 99999)
    assert exc_info.value.status_code == 404


def test_remove_user_from_company(db, test_user, test_admin):
    """Testa remover usuário de uma company"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    CompanyService.add_user_to_company(db, company.id, test_admin.id)
    
    updated_company = CompanyService.remove_user_from_company(db, company.id, test_admin.id)
    
    assert len(updated_company.users) == 1
    assert updated_company.users[0].id == test_user.id


def test_remove_user_from_company_not_member(db, test_user, test_admin):
    """Testa remover usuário que não é membro"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    
    with pytest.raises(HTTPException) as exc_info:
        CompanyService.remove_user_from_company(db, company.id, test_admin.id)
    assert exc_info.value.status_code == 400


def test_remove_user_from_company_not_found(db, test_user):
    """Testa remover usuário de company inexistente"""
    with pytest.raises(HTTPException) as exc_info:
        CompanyService.remove_user_from_company(db, 99999, test_user.id)
    assert exc_info.value.status_code == 404


def test_remove_user_from_company_user_not_found(db, test_user):
    """Testa remover usuário inexistente de company"""
    company_data = CompanyCreate(
        name="Test Company",
        user_id=test_user.id
    )
    company = CompanyService.create_company(db, company_data)
    
    with pytest.raises(HTTPException) as exc_info:
        CompanyService.remove_user_from_company(db, company.id, 99999)
    assert exc_info.value.status_code == 404

