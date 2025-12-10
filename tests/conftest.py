import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base, get_db
from core.security import create_access_token
from main import app
from apps.auth.models import UserRole
from apps.auth.services import UserService
from apps.auth.schemas import UserCreate


# Database de teste
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Cria um banco de dados de teste para cada teste"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Cria um cliente de teste"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Cria um usuário de teste"""
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        full_name="Test User"
    )
    return UserService.create_user(db, user_data, role=UserRole.USER)



@pytest.fixture
def test_admin(db):
    """Cria um admin de teste"""
    user_data = UserCreate(
        email="admin@example.com",
        username="admin",
        password="adminpass123",
        full_name="Admin User"
    )
    return UserService.create_user(db, user_data, role=UserRole.ADMIN)


@pytest.fixture
def user_token(test_user):
    """Gera token para usuário normal"""
    return create_access_token(data={"sub": test_user.id})


@pytest.fixture
def admin_token(test_admin):
    """Gera token para admin"""
    return create_access_token(data={"sub": test_admin.id})

