# Tourism Platform API Documentation

## Overview

The Tourism Platform API is a RESTful service built with FastAPI that provides comprehensive endpoints for managing tourist spots, reviews, accommodations, and user interactions.

**Base URL**: `http://localhost:8000`  
**API Version**: 1.0.0  
**Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)

---

## Authentication

### JWT Token Authentication

The API uses JWT (JSON Web Tokens) for authentication. Tokens are valid for 24 hours.

**Headers Required**:
```
Authorization: Bearer <your_jwt_token>
```

### Authentication Endpoints

#### Register New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "login": "username",
  "email": "user@example.com",
  "senha": "password123",
  "role": "USER"
}
```

**Response**: Returns access token and user details.

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "login": "username",
  "senha": "password123"
}
```

**Response**: Returns JWT access token.

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>
```

#### Logout
```http
POST /api/auth/logout
Authorization: Bearer <token>
```

---

## Tourist Spots

### List Tourist Spots
```http
GET /api/spots?skip=0&limit=20&cidade=Rio&estado=RJ&pais=Brasil&search=beach
```

**Query Parameters**:
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Max records to return (1-100, default: 20)
- `cidade` (string): Filter by city name
- `estado` (string): Filter by state name
- `pais` (string): Filter by country name
- `search` (string): Search in name and description

**Response**:
```json
{
  "spots": [
    {
      "id": 1,
      "nome": "Cristo Redentor",
      "descricao": "...",
      "cidade": "Rio de Janeiro",
      "estado": "RJ",
      "pais": "Brasil",
      "latitude": -22.9519,
      "longitude": -43.2105,
      "avg_rating": 4.8,
      "rating_count": 150,
      "photo_count": 25
    }
  ],
  "total": 1,
  "has_more": false
}
```

### Get Spot Details
```http
GET /api/spots/{spot_id}
```

### Create Spot (Admin Only)
```http
POST /api/spots
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "nome": "Spot Name",
  "descricao": "Description",
  "cidade": "City",
  "estado": "State",
  "pais": "Country",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "endereco": "Address"
}
```

### Update Spot (Admin Only)
```http
PUT /api/spots/{spot_id}
Authorization: Bearer <admin_token>
Content-Type: application/json
```

### Delete Spot (Admin Only)
```http
DELETE /api/spots/{spot_id}
Authorization: Bearer <admin_token>
```

**Note**: Performs soft delete.

### Get Directions
```http
GET /api/spots/{spot_id}/directions?from_latitude=-23.5505&from_longitude=-46.6333
```

### Export Spots (Admin Only)
```http
GET /api/spots/export?format=json&cidade=Rio
```

**Query Parameters**:
- `format`: "json" or "csv"
- `cidade`, `estado`, `pais`: Optional filters

### Import Spots (Admin Only)
```http
POST /api/spots/import?format=json
Content-Type: application/json

{
  "content": "<json_or_csv_string>"
}
```

---

## Photos

### Get Spot Photos
```http
GET /api/spots/{spot_id}/photos
```

### Upload Photo (Admin Only)
```http
POST /api/spots/{spot_id}/photos
Authorization: Bearer <admin_token>
Content-Type: multipart/form-data

file: <image_file>
titulo: "Photo Title"
```

### Delete Photo (Admin Only)
```http
DELETE /api/photos/{photo_id}
Authorization: Bearer <admin_token>
```

---

## Ratings & Reviews

### Get Spot Ratings
```http
GET /api/spots/{spot_id}/ratings?skip=0&limit=10
```

### Get Rating Statistics
```http
GET /api/spots/{spot_id}/ratings/stats
```

**Response**:
```json
{
  "average": 4.5,
  "total": 120,
  "1": 5,
  "2": 10,
  "3": 20,
  "4": 35,
  "5": 50
}
```

### Submit Rating (Authenticated)
```http
POST /api/spots/{spot_id}/ratings
Authorization: Bearer <token>
Content-Type: application/json

{
  "nota": 5,
  "comentario": "Amazing place!"
}
```

### Update Rating (Authenticated)
```http
PUT /api/ratings/{rating_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "nota": 4,
  "comentario": "Good but crowded"
}
```

---

## Comments

### Get Spot Comments
```http
GET /api/spots/{spot_id}/comments?skip=0&limit=20&sort_by=recent
```

**Query Parameters**:
- `sort_by`: "recent" or "likes"

### Post Comment (Authenticated)
```http
POST /api/spots/{spot_id}/comments
Authorization: Bearer <token>
Content-Type: application/json

{
  "texto": "Great experience!"
}
```

### Like Comment (Authenticated)
```http
POST /api/comments/{comment_id}/like
Authorization: Bearer <token>
```

### Report Comment (Authenticated)
```http
POST /api/comments/{comment_id}/report
Authorization: Bearer <token>
```

---

## Accommodations

### Get Spot Accommodations
```http
GET /api/spots/{spot_id}/accommodations?tipo=hotel&min_price=100&max_price=500
```

### Get Accommodation Statistics
```http
GET /api/spots/{spot_id}/accommodations/statistics
```

### Create Accommodation (Admin Only)
```http
POST /api/accommodations
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "ponto_id": 1,
  "nome": "Hotel Name",
  "endereco": "Address",
  "telefone": "+55 11 1234-5678",
  "preco_medio": 250.00,
  "tipo": "hotel",
  "link_reserva": "https://booking.com/..."
}
```

### Update Accommodation (Admin Only)
```http
PUT /api/accommodations/{accommodation_id}
Authorization: Bearer <admin_token>
```

### Delete Accommodation (Admin Only)
```http
DELETE /api/accommodations/{accommodation_id}
Authorization: Bearer <admin_token>
```

---

## Favorites

### Get User Favorites
```http
GET /api/favorites
Authorization: Bearer <token>
```

### Add to Favorites
```http
POST /api/spots/{spot_id}/favorite
Authorization: Bearer <token>
```

### Remove from Favorites
```http
DELETE /api/spots/{spot_id}/favorite
Authorization: Bearer <token>
```

### Toggle Favorite Status
```http
POST /api/spots/{spot_id}/favorite/toggle
Authorization: Bearer <token>
```

### Check Favorite Status
```http
GET /api/spots/{spot_id}/favorite/status
Authorization: Bearer <token>
```

---

## Health Checks

### Basic Health Check
```http
GET /health
```

### Readiness Check
```http
GET /health/ready
```

### Liveness Check
```http
GET /health/live
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": {
    "code": 400,
    "message": "Error description",
    "path": "/api/spots",
    "details": []  // Optional validation errors
  }
}
```

**Status Codes**:
- `200`: Success
- `201`: Created
- `204`: No Content (successful deletion)
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `422`: Validation Error
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

---

## Rate Limiting

**Limit**: 120 requests per minute per IP address

When exceeded, API returns `429 Too Many Requests`.

---

## Caching

- **Spot Details**: Cached for 5 minutes
- **Spot Lists**: Cached for 1 minute
- Cache is automatically invalidated on create/update/delete operations

---

## Data Formats

### Coordinates
- **Latitude**: -90 to 90 (6 decimal places)
- **Longitude**: -180 to 180 (6 decimal places)

### Ratings
- **Stars**: 1 to 5 (integer)
- **Comment**: Max 500 characters

### Photos
- **Formats**: JPEG, PNG, WebP
- **Max Size**: 5 MB per file
- **Max Count**: 10 photos per spot

---

## Best Practices

1. **Authentication**: Always include valid JWT token for protected endpoints
2. **Pagination**: Use `skip` and `limit` parameters for large datasets
3. **Error Handling**: Check response status codes and handle errors appropriately
4. **Rate Limiting**: Implement retry logic with exponential backoff
5. **Caching**: Cache responses on client side when appropriate

---

## Support

For issues or questions:
- GitHub Issues: [Repository Link]
- API Documentation: http://localhost:8000/docs
