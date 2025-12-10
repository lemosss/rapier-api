from apps.companies.models import Company
from apps.auth.models import User, UserRole


def test_company_model_creation(db):
    """Testa criação de modelo Company"""
    company = Company(
        name="Test Company",
        description="Test Description"
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    
    assert company.id is not None
    assert company.name == "Test Company"
    assert company.description == "Test Description"
    assert company.created_at is not None
    assert company.updated_at is not None


def test_company_user_relationship(db):
    """Testa relacionamento many-to-many entre Company e User"""
    # Cria usuário
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        role=UserRole.USER
    )
    db.add(user)
    db.flush()
    
    # Cria company
    company = Company(
        name="Test Company"
    )
    db.add(company)
    db.flush()
    
    # Associa usuário à company
    company.users.append(user)
    db.commit()
    db.refresh(company)
    db.refresh(user)
    
    assert len(company.users) == 1
    assert company.users[0].id == user.id
    assert len(user.companies) == 1
    assert user.companies[0].id == company.id


def test_company_multiple_users(db):
    """Testa company com múltiplos usuários"""
    # Cria usuários
    user1 = User(
        email="user1@example.com",
        username="user1",
        hashed_password="hashed_password",
        role=UserRole.USER
    )
    user2 = User(
        email="user2@example.com",
        username="user2",
        hashed_password="hashed_password",
        role=UserRole.USER
    )
    db.add_all([user1, user2])
    db.flush()
    
    # Cria company
    company = Company(name="Test Company")
    db.add(company)
    db.flush()
    
    # Associa usuários
    company.users.extend([user1, user2])
    db.commit()
    db.refresh(company)
    
    assert len(company.users) == 2


def test_user_multiple_companies(db):
    """Testa usuário com múltiplas companies"""
    # Cria usuário
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        role=UserRole.USER
    )
    db.add(user)
    db.flush()
    
    # Cria companies
    company1 = Company(name="Company 1")
    company2 = Company(name="Company 2")
    db.add_all([company1, company2])
    db.flush()
    
    # Associa companies ao usuário
    user.companies.extend([company1, company2])
    db.commit()
    db.refresh(user)
    
    assert len(user.companies) == 2

