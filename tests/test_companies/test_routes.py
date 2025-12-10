from fastapi import status
from apps.auth.models import UserRole
from apps.companies.services import CompanyService
from apps.companies.schemas import CompanyCreate
from apps.auth.services import UserService
from apps.auth.schemas import UserCreate


def test_create_company_as_admin(client, admin_token, test_user):
    """Testa criação de company como admin"""
    response = client.post(
        "/api/v1/companies",
        json={
            "name": "Test Company",
            "description": "Test Description",
            "user_id": test_user.id
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Test Company"
    assert data["description"] == "Test Description"
    assert "id" in data
    assert "created_at" in data


def test_create_company_unauthorized(client):
    """Testa criação de company sem autenticação"""
    response = client.post(
        "/api/v1/companies",
        json={
            "name": "Test Company",
            "user_id": 1
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_company_as_user(client, user_token, test_user):
    """Testa criação de company como usuário normal"""
    response = client.post(
        "/api/v1/companies",
        json={
            "name": "Test Company",
            "user_id": test_user.id
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_company_user_not_found(client, admin_token):
    """Testa criação de company com usuário inexistente"""
    response = client.post(
        "/api/v1/companies",
        json={
            "name": "Test Company",
            "user_id": 99999
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_my_companies(client, user_token, db, test_user):
    """Testa listagem de companies do usuário"""
    # Cria companies para o usuário
    company1_data = CompanyCreate(name="Company 1", user_id=test_user.id)
    company2_data = CompanyCreate(name="Company 2", user_id=test_user.id)
    CompanyService.create_company(db, company1_data)
    CompanyService.create_company(db, company2_data)
    
    response = client.get(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    company_names = [c["name"] for c in data]
    assert "Company 1" in company_names
    assert "Company 2" in company_names


def test_get_my_companies_empty(client, user_token):
    """Testa listagem quando usuário não tem companies"""
    response = client.get(
        "/api/v1/companies",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0


def test_get_my_companies_unauthorized(client):
    """Testa listagem de companies sem autenticação"""
    response = client.get("/api/v1/companies")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_company_as_member(client, user_token, db, test_user):
    """Testa obtenção de company como membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_user.id)
    company = CompanyService.create_company(db, company_data)
    
    response = client.get(
        f"/api/v1/companies/{company.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == company.id
    assert data["name"] == "Test Company"


def test_get_company_not_member(client, user_token, db, test_admin):
    """Testa obtenção de company quando não é membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_admin.id)
    company = CompanyService.create_company(db, company_data)
    
    response = client.get(
        f"/api/v1/companies/{company.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_company_not_found(client, user_token):
    """Testa obtenção de company inexistente"""
    response = client.get(
        "/api/v1/companies/99999",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_company_unauthorized(client):
    """Testa obtenção de company sem autenticação"""
    response = client.get("/api/v1/companies/1")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_company_as_member(client, user_token, db, test_user):
    """Testa atualização de company como membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_user.id)
    company = CompanyService.create_company(db, company_data)
    
    response = client.put(
        f"/api/v1/companies/{company.id}",
        json={
            "name": "Updated Company",
            "description": "New Description"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Company"
    assert data["description"] == "New Description"


def test_update_company_not_member(client, user_token, db, test_admin):
    """Testa atualização de company quando não é membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_admin.id)
    company = CompanyService.create_company(db, company_data)
    
    response = client.put(
        f"/api/v1/companies/{company.id}",
        json={"name": "Updated Company"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_company_not_found(client, user_token):
    """Testa atualização de company inexistente"""
    response = client.put(
        "/api/v1/companies/99999",
        json={"name": "Updated Company"},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_add_user_to_company_as_member(client, user_token, db, test_user, test_admin):
    """Testa adicionar usuário a company como membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_user.id)
    company = CompanyService.create_company(db, company_data)
    
    response = client.post(
        f"/api/v1/companies/{company.id}/users",
        json={"user_id": test_admin.id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["users"]) == 2
    user_ids = [u["id"] for u in data["users"]]
    assert test_user.id in user_ids
    assert test_admin.id in user_ids


def test_add_user_to_company_not_member(client, user_token, db, test_admin):
    """Testa adicionar usuário quando não é membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_admin.id)
    company = CompanyService.create_company(db, company_data)
    
    # Cria outro usuário
    user_data = UserCreate(
        email="newuser@example.com",
        username="newuser",
        password="password123"
    )
    new_user = UserService.create_user(db, user_data)
    
    response = client.post(
        f"/api/v1/companies/{company.id}/users",
        json={"user_id": new_user.id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_add_user_to_company_already_member(client, user_token, db, test_user):
    """Testa adicionar usuário que já é membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_user.id)
    company = CompanyService.create_company(db, company_data)
    
    response = client.post(
        f"/api/v1/companies/{company.id}/users",
        json={"user_id": test_user.id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_add_user_to_company_user_not_found(client, user_token, db, test_user):
    """Testa adicionar usuário inexistente"""
    company_data = CompanyCreate(name="Test Company", user_id=test_user.id)
    company = CompanyService.create_company(db, company_data)
    
    response = client.post(
        f"/api/v1/companies/{company.id}/users",
        json={"user_id": 99999},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_user_from_company_as_member(client, user_token, db, test_user, test_admin):
    """Testa remover usuário de company como membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_user.id)
    company = CompanyService.create_company(db, company_data)
    CompanyService.add_user_to_company(db, company.id, test_admin.id)
    
    response = client.delete(
        f"/api/v1/companies/{company.id}/users/{test_admin.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["users"]) == 1
    assert data["users"][0]["id"] == test_user.id


def test_remove_user_from_company_not_member(client, user_token, db, test_admin):
    """Testa remover usuário quando não é membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_admin.id)
    company = CompanyService.create_company(db, company_data)
    
    response = client.delete(
        f"/api/v1/companies/{company.id}/users/{test_admin.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_remove_user_from_company_not_found(client, user_token, db, test_user):
    """Testa remover usuário de company inexistente"""
    response = client.delete(
        "/api/v1/companies/99999/users/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_user_from_company_user_not_member(client, user_token, db, test_user, test_admin):
    """Testa remover usuário que não é membro"""
    company_data = CompanyCreate(name="Test Company", user_id=test_user.id)
    company = CompanyService.create_company(db, company_data)
    
    response = client.delete(
        f"/api/v1/companies/{company.id}/users/{test_admin.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

