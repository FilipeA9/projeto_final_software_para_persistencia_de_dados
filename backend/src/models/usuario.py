"""
Usuario SQLAlchemy model - User entity for authentication and authorization.

Represents users in the tourism platform with role-based access control.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
import enum

from src.config.postgres import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    USER = "USER"
    ADMIN = "ADMIN"


class Usuario(Base):
    """
    Usuario model - User entity for authentication.
    
    Attributes:
        id: Primary key.
        login: Unique username for authentication.
        email: Unique email address.
        senha_hash: Bcrypt password hash.
        role: User role (USER or ADMIN).
        created_at: Account creation timestamp.
    """
    
    __tablename__ = "usuario"
    
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.USER, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    pontos_turisticos = relationship("PontoTuristico", back_populates="criador", cascade="all, delete-orphan")
    avaliacoes = relationship("Avaliacao", back_populates="usuario", cascade="all, delete-orphan")
    favoritos = relationship("Favorito", back_populates="usuario", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Usuario(id={self.id}, login='{self.login}', role='{self.role.value}')>"
