import pytest
from core.config import settings


def test_settings_loaded():
    """Testa se as configurações foram carregadas"""
    assert settings.APP_NAME is not None
    assert settings.SECRET_KEY is not None
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0


def test_database_url():
    """Testa URL do banco de dados"""
    assert settings.DATABASE_URL is not None
    assert isinstance(settings.DATABASE_URL, str)

