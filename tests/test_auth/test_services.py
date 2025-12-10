import pytest
from fastapi import HTTPException
from apps.auth.services import UserService
from apps.auth.schemas import UserCreate, UserUpdate
from apps.auth.models import UserRole


def test_create_user(db):
    """Testa criação de usuário"""
    user_data = UserCreate(
        email="new@example.com",
        username="newuser",
        password="password123",
        full_name="New User"
    )
    user = UserService.create_user(db, user_data)
    
    assert user.id is not None
    assert user.email == "new@example.com"
    assert user.username == "newuser"
    assert user.role == UserRole.USER
    assert user.hashed_password != "password123"  # Deve estar hasheado


def test_create_user_duplicate_email(db, test_user):
    """Testa criação de usuário com email duplicado"""
    user_data = UserCreate(
        email=test_user.email,
        username="different",
        password="password123"
    )
    with pytest.raises(HTTPException) as exc_info:
        UserService.create_user(db, user_data)
    assert exc_info.value.status_code == 400


def test_create_user_duplicate_username(db, test_user):
    """Testa criação de usuário com username duplicado"""
    user_data = UserCreate(
        email="different@example.com",
        username=test_user.username,
        password="password123"
    )
    with pytest.raises(HTTPException) as exc_info:
        UserService.create_user(db, user_data)
    assert exc_info.value.status_code == 400


def test_create_user_admin_role(db):
    """Testa criação de usuário com role admin"""
    user_data = UserCreate(
        email="admin@example.com",
        username="adminuser",
        password="password123"
    )
    user = UserService.create_user(db, user_data, role=UserRole.ADMIN)
    assert user.role == UserRole.ADMIN


def test_get_user_by_id(db, test_user):
    """Testa obtenção de usuário por ID"""
    user = UserService.get_user_by_id(db, test_user.id)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


def test_get_user_by_id_not_found(db):
    """Testa obtenção de usuário inexistente"""
    user = UserService.get_user_by_id(db, 99999)
    assert user is None


def test_get_user_by_email(db, test_user):
    """Testa obtenção de usuário por email"""
    user = UserService.get_user_by_email(db, test_user.email)
    assert user is not None
    assert user.email == test_user.email


def test_get_user_by_username(db, test_user):
    """Testa obtenção de usuário por username"""
    user = UserService.get_user_by_username(db, test_user.username)
    assert user is not None
    assert user.username == test_user.username


def test_get_all_users(db, test_user, test_admin):
    """Testa listagem de todos os usuários"""
    users = UserService.get_all_users(db)
    assert len(users) >= 2
    user_ids = [u.id for u in users]
    assert test_user.id in user_ids
    assert test_admin.id in user_ids


def test_get_all_users_pagination(db):
    """Testa paginação na listagem de usuários"""
    # Cria múltiplos usuários
    for i in range(5):
        user_data = UserCreate(
            email=f"user{i}@example.com",
            username=f"user{i}",
            password="password123"
        )
        UserService.create_user(db, user_data)
    
    users = UserService.get_all_users(db, skip=0, limit=3)
    assert len(users) == 3
    
    users = UserService.get_all_users(db, skip=3, limit=3)
    assert len(users) == 2


def test_update_user(db, test_user):
    """Testa atualização de usuário"""
    user_update = UserUpdate(
        email="updated@example.com",
        full_name="Updated Name"
    )
    updated_user = UserService.update_user(db, test_user.id, user_update)
    
    assert updated_user.email == "updated@example.com"
    assert updated_user.full_name == "Updated Name"
    assert updated_user.username == test_user.username  # Não mudou


def test_update_user_password(db, test_user):
    """Testa atualização de senha"""
    # Salva o hash original antes de atualizar
    original_hash = test_user.hashed_password
    
    user_update = UserUpdate(password="newpassword123")
    updated_user = UserService.update_user(db, test_user.id, user_update)
    
    assert updated_user.hashed_password != original_hash
    # Verifica se a nova senha funciona
    from core.security import verify_password
    assert verify_password("newpassword123", updated_user.hashed_password)


def test_update_user_not_found(db):
    """Testa atualização de usuário inexistente"""
    user_update = UserUpdate(email="new@example.com")
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_user(db, 99999, user_update)
    assert exc_info.value.status_code == 404


def test_update_user_duplicate_email(db, test_user, test_admin):
    """Testa atualização com email duplicado"""
    user_update = UserUpdate(email=test_admin.email)
    with pytest.raises(HTTPException) as exc_info:
        UserService.update_user(db, test_user.id, user_update)
    assert exc_info.value.status_code == 400


def test_delete_user(db, test_user):
    """Testa deleção de usuário"""
    user_id = test_user.id
    result = UserService.delete_user(db, user_id)
    
    assert result is True
    deleted_user = UserService.get_user_by_id(db, user_id)
    assert deleted_user is None


def test_delete_user_not_found(db):
    """Testa deleção de usuário inexistente"""
    with pytest.raises(HTTPException) as exc_info:
        UserService.delete_user(db, 99999)
    assert exc_info.value.status_code == 404


def test_authenticate_user_success(db, test_user):
    """Testa autenticação bem-sucedida"""
    user = UserService.authenticate_user(db, test_user.username, "testpass123")
    assert user is not None
    assert user.id == test_user.id


def test_authenticate_user_wrong_password(db, test_user):
    """Testa autenticação com senha errada"""
    user = UserService.authenticate_user(db, test_user.username, "wrongpassword")
    assert user is None


def test_authenticate_user_not_found(db):
    """Testa autenticação com usuário inexistente"""
    user = UserService.authenticate_user(db, "nonexistent", "password")
    assert user is None

