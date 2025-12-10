from apps.auth.models import User, UserRole


def test_user_model_creation(db):
    """Testa criação de modelo User"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.role == UserRole.USER
    assert user.is_active is True


def test_user_model_defaults(db):
    """Testa valores padrão do modelo User"""
    user = User(
        email="test2@example.com",
        username="testuser2",
        hashed_password="hashed_password"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.is_active is True
    assert user.role == UserRole.USER

