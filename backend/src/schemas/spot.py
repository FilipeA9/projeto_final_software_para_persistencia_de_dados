"""
Pydantic schemas for tourist spot requests and responses.
"""

from typing import Optional
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime


class SpotBase(BaseModel):
    """Base schema for tourist spot."""
    nome: str = Field(..., min_length=1, max_length=255)
    descricao: str = Field(..., min_length=1)
    cidade: str = Field(..., min_length=1, max_length=100)
    estado: str = Field(..., min_length=1, max_length=100)
    pais: str = Field(..., min_length=1, max_length=100)
    latitude: Decimal = Field(..., ge=-90, le=90)
    longitude: Decimal = Field(..., ge=-180, le=180)
    endereco: str = Field(..., min_length=1)


class CreateSpotRequest(SpotBase):
    """Schema for creating a new tourist spot."""
    pass


class UpdateSpotRequest(BaseModel):
    """Schema for updating an existing tourist spot."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    descricao: Optional[str] = Field(None, min_length=1)
    cidade: Optional[str] = Field(None, min_length=1, max_length=100)
    estado: Optional[str] = Field(None, min_length=1, max_length=100)
    pais: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[Decimal] = Field(None, ge=-90, le=90)
    longitude: Optional[Decimal] = Field(None, ge=-180, le=180)
    endereco: Optional[str] = Field(None, min_length=1)


class SpotListItem(BaseModel):
    """Schema for spot in list view (summary)."""
    id: int
    nome: str
    descricao: str  # Truncated
    cidade: str
    estado: str
    pais: str
    avg_rating: Optional[float] = None
    rating_count: int


class SpotDetail(BaseModel):
    """Schema for spot detail view (full data)."""
    id: int
    nome: str
    descricao: str
    cidade: str
    estado: str
    pais: str
    latitude: float
    longitude: float
    endereco: str
    criado_por: int
    created_at: str
    avg_rating: Optional[float] = None
    rating_count: int
    photo_count: int


class SpotListResponse(BaseModel):
    """Schema for paginated spot list response."""
    spots: list[SpotListItem]
    total: int
    skip: int
    limit: int
    has_more: bool


class PhotoResponse(BaseModel):
    """Schema for photo response."""
    id: str
    titulo: str
    filename: str
    url: str
    thumbnail_url: str
    uploaded_by: int
    created_at: str


class RatingResponse(BaseModel):
    """Schema for rating response."""
    id: int
    ponto_id: int
    usuario_id: int
    nota: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RatingDistributionResponse(BaseModel):
    """Schema for rating distribution."""
    stars_1: int = Field(..., alias="1")
    stars_2: int = Field(..., alias="2")
    stars_3: int = Field(..., alias="3")
    stars_4: int = Field(..., alias="4")
    stars_5: int = Field(..., alias="5")
    average: Optional[float]
    total: int
    
    class Config:
        populate_by_name = True


class CreateRatingRequest(BaseModel):
    """Schema for creating a new rating."""
    nota: int = Field(..., ge=1, le=5, description="Rating value (1-5 stars)")
    comentario: Optional[str] = Field(None, max_length=1000, description="Optional review comment")


class UpdateRatingRequest(BaseModel):
    """Schema for updating an existing rating."""
    nota: Optional[int] = Field(None, ge=1, le=5, description="Rating value (1-5 stars)")
    comentario: Optional[str] = Field(None, max_length=1000, description="Optional review comment")


class CommentResponse(BaseModel):
    """Schema for comment response."""
    id: str = Field(..., alias="_id")
    pontoId: int
    usuarioId: int
    texto: str
    createdAt: datetime
    metadata: dict = Field(default_factory=lambda: {"likes": 0, "reports": 0})
    usuario: Optional[dict] = None
    
    class Config:
        populate_by_name = True


class CreateCommentRequest(BaseModel):
    """Schema for creating a new comment."""
    texto: str = Field(..., min_length=1, max_length=2000, description="Comment text")


class CommentListResponse(BaseModel):
    """Schema for paginated comment list response."""
    comments: list[CommentResponse]
    pagination: dict


# Accommodation schemas
class AccommodationBase(BaseModel):
    """Base schema for accommodation."""
    nome: str = Field(..., min_length=1, max_length=255)
    endereco: str = Field(..., min_length=1)
    tipo: str = Field(..., pattern="^(hotel|pousada|hostel)$")
    telefone: Optional[str] = Field(None, max_length=20)
    preco_medio: Optional[float] = Field(None, ge=0)
    link_reserva: Optional[str] = None


class CreateAccommodationRequest(AccommodationBase):
    """Schema for creating a new accommodation."""
    ponto_id: int = Field(..., gt=0)


class UpdateAccommodationRequest(BaseModel):
    """Schema for updating an existing accommodation."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    endereco: Optional[str] = Field(None, min_length=1)
    tipo: Optional[str] = Field(None, pattern="^(hotel|pousada|hostel)$")
    telefone: Optional[str] = Field(None, max_length=20)
    preco_medio: Optional[float] = Field(None, ge=0)
    link_reserva: Optional[str] = None


class AccommodationResponse(BaseModel):
    """Schema for accommodation response."""
    id: int
    ponto_id: int
    nome: str
    endereco: str
    telefone: Optional[str]
    preco_medio: Optional[float]
    tipo: str
    link_reserva: Optional[str]
    
    class Config:
        from_attributes = True


class AccommodationListResponse(BaseModel):
    """Schema for accommodation list response."""
    accommodations: list[AccommodationResponse]
    total: int


class AccommodationStatisticsResponse(BaseModel):
    """Schema for accommodation statistics."""
    total: int
    avg_price: float
    min_price: float
    max_price: float
    types: dict
