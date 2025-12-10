import pytest
from datetime import timedelta
from jose import jwt
from core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from core.config import settings


def test_password_hashing():
    """Testa hash de senha"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert len(hashed) > 0


def test_password_verification():
    """Testa verificação de senha"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token():
    """Testa criação de token JWT"""
    data = {"sub": 1, "username": "testuser"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_with_expires():
    """Testa criação de token com expiração customizada"""
    data = {"sub": 1}
    expires = timedelta(minutes=60)
    token = create_access_token(data, expires_delta=expires)
    
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "exp" in payload
    assert "sub" in payload
    assert payload["sub"] == "1"  # JWT converte para string


def test_decode_access_token_success():
    """Testa decodificação de token válido"""
    data = {"sub": 1, "username": "testuser"}
    token = create_access_token(data)
    
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "1"  # JWT converte para string
    assert payload["username"] == "testuser"


def test_decode_access_token_invalid():
    """Testa decodificação de token inválido"""
    invalid_token = "invalid.token.here"
    payload = decode_access_token(invalid_token)
    assert payload is None


def test_decode_access_token_expired():
    """Testa decodificação de token expirado"""
    from datetime import datetime, timedelta, timezone
    
    data = {"sub": "1"}
    # Token expirado há 1 hora
    expire = datetime.now(timezone.utc) - timedelta(hours=1)
    data["exp"] = expire
    
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    payload = decode_access_token(token)
    assert payload is None

