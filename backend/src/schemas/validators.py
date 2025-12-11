"""
Validation Schemas - Comprehensive input validation for tourist spot data.

Provides Pydantic validators for all data inputs.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum


class AccommodationType(str, Enum):
    """Accommodation type enumeration."""
    HOTEL = "hotel"
    POUSADA = "pousada"
    HOSTEL = "hostel"


class CoordinateValidator(BaseModel):
    """Validator for geographic coordinates."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude (-90 to 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude (-180 to 180)")
    
    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90')
        return round(v, 6)  # Limit precision to 6 decimal places
    
    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180')
        return round(v, 6)  # Limit precision to 6 decimal places


class SpotValidator(BaseModel):
    """Validator for tourist spot creation/update."""
    
    nome: str = Field(..., min_length=3, max_length=200, description="Spot name")
    descricao: Optional[str] = Field(None, max_length=2000, description="Spot description")
    cidade: str = Field(..., min_length=2, max_length=100, description="City name")
    estado: str = Field(..., min_length=2, max_length=100, description="State name")
    pais: str = Field(..., min_length=2, max_length=100, description="Country name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    endereco: Optional[str] = Field(None, max_length=500, description="Address")
    
    @validator('nome')
    def validate_nome(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome cannot be empty')
        return v.strip()
    
    @validator('cidade', 'estado', 'pais')
    def validate_location_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Location fields cannot be empty')
        return v.strip()


class RatingValidator(BaseModel):
    """Validator for rating submission."""
    
    nota: int = Field(..., ge=1, le=5, description="Rating (1-5 stars)")
    comentario: Optional[str] = Field(None, max_length=500, description="Comment")
    
    @validator('comentario')
    def validate_comentario(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) > 500:
                raise ValueError('Comentario must be 500 characters or less')
            return v if v else None
        return None


class CommentValidator(BaseModel):
    """Validator for comment submission."""
    
    texto: str = Field(..., min_length=1, max_length=1000, description="Comment text")
    
    @validator('texto')
    def validate_texto(cls, v):
        if not v or not v.strip():
            raise ValueError('Comment text cannot be empty')
        v = v.strip()
        if len(v) > 1000:
            raise ValueError('Comment must be 1000 characters or less')
        return v


class AccommodationValidator(BaseModel):
    """Validator for accommodation creation/update."""
    
    nome: str = Field(..., min_length=3, max_length=200, description="Accommodation name")
    endereco: str = Field(..., min_length=5, max_length=500, description="Address")
    telefone: Optional[str] = Field(None, max_length=20, description="Phone number")
    preco_medio: Optional[float] = Field(None, ge=0, description="Average price")
    tipo: AccommodationType = Field(..., description="Accommodation type")
    link_reserva: Optional[str] = Field(None, max_length=500, description="Booking link")
    
    @validator('nome', 'endereco')
    def validate_text_fields(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()
    
    @validator('telefone')
    def validate_telefone(cls, v):
        if v is not None:
            v = v.strip()
            # Remove common separators
            cleaned = ''.join(c for c in v if c.isdigit() or c in ['+', '-', '(', ')', ' '])
            if not cleaned:
                return None
            return cleaned
        return None
    
    @validator('link_reserva')
    def validate_link(cls, v):
        if v is not None:
            v = v.strip()
            if v and not (v.startswith('http://') or v.startswith('https://')):
                raise ValueError('Link must start with http:// or https://')
            return v if v else None
        return None


class PhotoValidator(BaseModel):
    """Validator for photo metadata."""
    
    titulo: Optional[str] = Field(None, max_length=200, description="Photo title")
    filename: str = Field(..., min_length=1, max_length=255, description="Filename")
    
    @validator('titulo')
    def validate_titulo(cls, v):
        if v is not None:
            v = v.strip()
            return v if v else None
        return None
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or not v.strip():
            raise ValueError('Filename cannot be empty')
        
        # Check file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f'Invalid file extension. Allowed: {", ".join(allowed_extensions)}')
        
        return v.strip()


class PaginationValidator(BaseModel):
    """Validator for pagination parameters."""
    
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(20, ge=1, le=100, description="Max records to return")
    
    @validator('limit')
    def validate_limit(cls, v):
        if v > 100:
            return 100  # Cap at 100
        return v
