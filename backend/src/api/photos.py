"""
Photos API endpoints - Photo retrieval for tourist spots.

Implements GET endpoints for viewing photos.
"""

from fastapi import APIRouter, HTTPException, status

from src.services.photo_service import PhotoService
from src.schemas.spot import PhotoResponse

router = APIRouter()


@router.get("/spots/{spot_id}/photos", response_model=list[PhotoResponse])
async def get_spot_photos(spot_id: int):
    """
    Get all photos for a tourist spot.
    
    **Returns:**
    - List of photos with URLs and metadata
    - Thumbnail URLs for optimized loading
    - Upload timestamp and uploader ID
    
    **Response includes:**
    - `url`: Full-size photo URL
    - `thumbnail_url`: Thumbnail (300x300) URL
    - `titulo`: Optional photo title/caption
    - `uploaded_by`: User ID who uploaded the photo
    - `created_at`: Upload timestamp (ISO 8601)
    
    **Photo storage:**
    - Files stored in `/uploads/{spot_id}/` directory
    - Metadata stored in MongoDB `fotos` collection
    - Thumbnails generated automatically on upload
    
    **Note:** Returns empty list if spot has no photos.
    """
    service = PhotoService()
    photos = await service.get_photos_by_spot(spot_id)
    return photos


@router.get("/photos/{photo_id}", response_model=PhotoResponse)
async def get_photo(photo_id: str):
    """
    Get photo details by ID.
    
    **Args:**
    - `photo_id`: MongoDB ObjectId of the photo
    
    **Returns:**
    - Photo details with URLs and metadata
    
    **Errors:**
    - 404: Photo not found
    """
    service = PhotoService()
    photo = await service.get_photo_by_id(photo_id)
    
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Photo with ID {photo_id} not found",
        )
    
    return photo
