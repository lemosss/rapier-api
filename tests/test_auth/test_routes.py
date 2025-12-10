from fastapi import status
from apps.auth.models import UserRole


def test_register_user(client):
    """Testa registro de novo usuário"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert data["role"] == UserRole.USER.value
    assert "password" not in data


def test_register_user_duplicate_email(client, test_user):
    """Testa registro com email duplicado"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,
            "username": "different",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_user_duplicate_username(client, test_user):
    """Testa registro com username duplicado"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "different@example.com",
            "username": test_user.username,
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_admin_unauthorized(client):
    """Testa registro de admin sem autenticação"""
    response = client.post(
        "/api/v1/auth/register/admin",
        json={
            "email": "admin@example.com",
            "username": "adminuser",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_admin_as_user(client, user_token):
    """Testa registro de admin como usuário normal"""
    response = client.post(
        "/api/v1/auth/register/admin",
        json={
            "email": "admin@example.com",
            "username": "adminuser",
            "password": "password123"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_register_admin_as_admin(client, admin_token):
    """Testa registro de admin como admin"""
    response = client.post(
        "/api/v1/auth/register/admin",
        json={
            "email": "newadmin@example.com",
            "username": "newadmin",
            "password": "password123"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["role"] == UserRole.ADMIN.value


def test_login_success(client, test_user):
    """Testa login bem-sucedido"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Testa login com senha errada"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_wrong_username(client):
    """Testa login com username errado"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_inactive_user(client, db, test_user):
    """Testa login com usuário inativo"""
    from apps.auth.services import UserService
    from apps.auth.schemas import UserUpdate
    
    UserService.update_user(db, test_user.id, UserUpdate(is_active=False))
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_current_user_info(client, user_token, test_user):
    """Testa obtenção de informações do usuário atual"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_get_current_user_info_unauthorized(client):
    """Testa obtenção de informações sem token"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_all_users_unauthorized(client):
    """Testa listagem de usuários sem autenticação"""
    response = client.get("/api/v1/auth/users")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_all_users_as_user(client, user_token):
    """Testa listagem de usuários como usuário normal"""
    response = client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_all_users_as_admin(client, admin_token, test_user, test_admin):
    """Testa listagem de usuários como admin"""
    response = client.get(
        "/api/v1/auth/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2
    user_ids = [u["id"] for u in data]
    assert test_user.id in user_ids
    assert test_admin.id in user_ids


def test_get_user_by_id_as_admin(client, admin_token, test_user):
    """Testa obtenção de usuário por ID como admin"""
    response = client.get(
        f"/api/v1/auth/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id


def test_get_user_by_id_not_found(client, admin_token):
    """Testa obtenção de usuário inexistente"""
    response = client.get(
        "/api/v1/auth/users/99999",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_user_as_admin(client, admin_token, test_user):
    """Testa atualização de usuário como admin"""
    response = client.put(
        f"/api/v1/auth/users/{test_user.id}",
        json={
            "email": "updated@example.com",
            "full_name": "Updated Name"
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["full_name"] == "Updated Name"


def test_update_current_user(client, user_token, test_user):
    """Testa atualização do próprio usuário"""
    response = client.put(
        "/api/v1/auth/me",
        json={
            "full_name": "My New Name"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "My New Name"


def test_update_current_user_cannot_change_role(client, user_token):
    """Testa que usuário não pode mudar sua própria role"""
    response = client.put(
        "/api/v1/auth/me",
        json={
            "role": "admin"
        },
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # A role não deve mudar mesmo que enviada
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["role"] == UserRole.USER.value  # Permanece como user


def test_delete_user_as_admin(client, admin_token, db):
    """Testa deleção de usuário como admin"""
    from apps.auth.services import UserService
    from apps.auth.schemas import UserCreate
    
    # Cria usuário para deletar
    user_data = UserCreate(
        email="todelete@example.com",
        username="todelete",
        password="password123"
    )
    user = UserService.create_user(db, user_data)
    
    response = client.delete(
        f"/api/v1/auth/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verifica se foi deletado
    deleted_user = UserService.get_user_by_id(db, user.id)
    assert deleted_user is None


def test_delete_user_unauthorized(client, user_token, test_user):
    """Testa deleção de usuário sem permissão"""
    response = client.delete(
        f"/api/v1/auth/users/{test_user.id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

