"""
PontoTuristico SQLAlchemy model - Tourist spot entity.

Represents tourist attractions and destinations with location data.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from src.config.postgres import Base


class PontoTuristico(Base):
    """
    PontoTuristico model - Tourist spot entity.
    
    Attributes:
        id: Primary key.
        nome: Name of the tourist spot.
        descricao: Detailed description.
        cidade: City name.
        estado: State/province name.
        pais: Country name.
        latitude: Geographic latitude (-90 to 90).
        longitude: Geographic longitude (-180 to 180).
        endereco: Full address.
        criado_por: Foreign key to Usuario who created this spot.
        created_at: Creation timestamp.
        deleted_at: Soft delete timestamp (NULL if active).
    """
    
    __tablename__ = "ponto_turistico"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    cidade = Column(String(100), nullable=False, index=True)
    estado = Column(String(100), nullable=False, index=True)
    pais = Column(String(100), nullable=False, index=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    endereco = Column(Text, nullable=False)
    criado_por = Column(Integer, ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True, index=True)
    
    # Check constraints
    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="ponto_latitude_check"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="ponto_longitude_check"),
    )
    
    # Relationships
    criador = relationship("Usuario", back_populates="pontos_turisticos")
    hospedagens = relationship("Hospedagem", back_populates="ponto", cascade="all, delete-orphan")
    avaliacoes = relationship("Avaliacao", back_populates="ponto", cascade="all, delete-orphan")
    favoritos = relationship("Favorito", back_populates="ponto", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<PontoTuristico(id={self.id}, nome='{self.nome}', cidade='{self.cidade}')>"
