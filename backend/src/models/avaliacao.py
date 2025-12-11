"""
Avaliacao SQLAlchemy model - Rating/review entity.

Represents user ratings for tourist spots with optional comments.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship

from src.config.postgres import Base


class Avaliacao(Base):
    """
    Avaliacao model - Rating/review entity.
    
    Attributes:
        id: Primary key.
        ponto_id: Foreign key to PontoTuristico.
        usuario_id: Foreign key to Usuario.
        nota: Rating value (1-5 stars).
        comentario: Optional review comment.
        created_at: Rating creation timestamp.
    """
    
    __tablename__ = "avaliacao"
    
    id = Column(Integer, primary_key=True, index=True)
    ponto_id = Column(Integer, ForeignKey("ponto_turistico.id", ondelete="CASCADE"), nullable=False, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False, index=True)
    nota = Column(Integer, nullable=False, index=True)
    comentario = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Check constraints
    __table_args__ = (
        CheckConstraint("nota BETWEEN 1 AND 5", name="avaliacao_nota_check"),
        UniqueConstraint("ponto_id", "usuario_id", name="avaliacao_unique_user_spot"),
    )
    
    # Relationships
    ponto = relationship("PontoTuristico", back_populates="avaliacoes")
    usuario = relationship("Usuario", back_populates="avaliacoes")
    
    def __repr__(self) -> str:
        return f"<Avaliacao(id={self.id}, ponto_id={self.ponto_id}, nota={self.nota})>"
