"""
Favorito SQLAlchemy model - User favorites entity.

Represents user's favorite tourist spots for quick access.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from src.config.postgres import Base


class Favorito(Base):
    """
    Favorito model - User favorites entity.
    
    Attributes:
        id: Primary key.
        usuario_id: Foreign key to Usuario.
        ponto_id: Foreign key to PontoTuristico.
        created_at: Favorite creation timestamp.
    """
    
    __tablename__ = "favorito"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True)
    ponto_id = Column(Integer, ForeignKey("ponto_turistico.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Unique constraint - one favorite per user per spot
    __table_args__ = (
        UniqueConstraint("usuario_id", "ponto_id", name="favorito_unique_user_spot"),
    )
    
    # Relationships
    usuario = relationship("Usuario", back_populates="favoritos")
    ponto = relationship("PontoTuristico", back_populates="favoritos")
    
    def __repr__(self) -> str:
        return f"<Favorito(id={self.id}, usuario_id={self.usuario_id}, ponto_id={self.ponto_id})>"
