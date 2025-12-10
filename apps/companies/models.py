from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from core.database import Base

# Importar User para o relacionamento (evita import circular)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from apps.auth.models import User

# Tabela de associação many-to-many entre User e Company
user_companies = Table(
    'user_companies',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('company_id', Integer, ForeignKey('companies.id'), primary_key=True)
)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relacionamento many-to-many com User
    users = relationship("User", secondary=user_companies, back_populates="companies")

