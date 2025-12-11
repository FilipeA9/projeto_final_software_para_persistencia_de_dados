"""
Hospedagem SQLAlchemy model - Accommodation entity.

Represents hotels, hostels, and lodgings near tourist spots.
"""

from decimal import Decimal
from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship
import enum

from src.config.postgres import Base


class TipoHospedagem(str, enum.Enum):
    """Accommodation type enumeration."""
    HOTEL = "hotel"
    POUSADA = "pousada"
    HOSTEL = "hostel"


class Hospedagem(Base):
    """
    Hospedagem model - Accommodation entity.
    
    Attributes:
        id: Primary key.
        ponto_id: Foreign key to PontoTuristico.
        nome: Name of the accommodation.
        endereco: Full address.
        telefone: Contact phone number.
        preco_medio: Average price per night.
        tipo: Type of accommodation (hotel, pousada, hostel).
        link_reserva: Booking/reservation URL.
    """
    
    __tablename__ = "hospedagem"
    
    id = Column(Integer, primary_key=True, index=True)
    ponto_id = Column(Integer, ForeignKey("ponto_turistico.id", ondelete="CASCADE"), nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    endereco = Column(Text, nullable=False)
    telefone = Column(String(20), nullable=True)
    preco_medio = Column(Numeric(10, 2), nullable=True, index=True)
    tipo = Column(Enum(TipoHospedagem, name="tipo_hospedagem"), nullable=False, index=True)
    link_reserva = Column(Text, nullable=True)
    
    # Check constraints
    __table_args__ = (
        CheckConstraint("preco_medio >= 0", name="hospedagem_preco_check"),
    )
    
    # Relationships
    ponto = relationship("PontoTuristico", back_populates="hospedagens")
    
    def __repr__(self) -> str:
        return f"<Hospedagem(id={self.id}, nome='{self.nome}', tipo='{self.tipo.value}')>"
