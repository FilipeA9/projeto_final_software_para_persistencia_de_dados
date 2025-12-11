"""
API client for backend communication.

Provides typed interface to Turistando API endpoints.
"""

import requests
from typing import Optional, List, Dict, Any


class TuristandoAPI:
    """Client for Turistando API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_prefix = "/api"
        self.session = requests.Session()
    
    def _url(self, path: str) -> str:
        """Build full URL for API endpoint."""
        return f"{self.base_url}{self.api_prefix}{path}"
    
    def list_spots(
        self,
        skip: int = 0,
        limit: int = 20,
        cidade: Optional[str] = None,
        estado: Optional[str] = None,
        pais: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List tourist spots with filters.
        
        Args:
            skip: Records to skip.
            limit: Max records.
            cidade: Filter by city.
            estado: Filter by state.
            pais: Filter by country.
            search: Search query.
        
        Returns:
            API response with spots list.
        """
        params = {"skip": skip, "limit": limit}
        if cidade:
            params["cidade"] = cidade
        if estado:
            params["estado"] = estado
        if pais:
            params["pais"] = pais
        if search:
            params["search"] = search
        
        response = self.session.get(self._url("/spots"), params=params)
        response.raise_for_status()
        return response.json()
    
    def get_spot(self, spot_id: int) -> Dict[str, Any]:
        """
        Get spot details by ID.
        
        Args:
            spot_id: Spot ID.
        
        Returns:
            Spot details.
        """
        response = self.session.get(self._url(f"/spots/{spot_id}"))
        response.raise_for_status()
        return response.json()
    
    def get_spot_photos(self, spot_id: int) -> List[Dict[str, Any]]:
        """
        Get photos for a spot.
        
        Args:
            spot_id: Spot ID.
        
        Returns:
            List of photos.
        """
        response = self.session.get(self._url(f"/spots/{spot_id}/photos"))
        response.raise_for_status()
        return response.json()
    
    def get_spot_ratings(
        self, spot_id: int, skip: int = 0, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get ratings for a spot.
        
        Args:
            spot_id: Spot ID.
            skip: Records to skip.
            limit: Max records.
        
        Returns:
            List of ratings.
        """
        params = {"skip": skip, "limit": limit}
        response = self.session.get(self._url(f"/spots/{spot_id}/ratings"), params=params)
        response.raise_for_status()
        return response.json()
    
    def get_spot_rating_stats(self, spot_id: int) -> Dict[str, Any]:
        """
        Get rating statistics for a spot.
        
        Args:
            spot_id: Spot ID.
        
        Returns:
            Rating distribution and average.
        """
        response = self.session.get(self._url(f"/spots/{spot_id}/ratings/stats"))
        response.raise_for_status()
        return response.json()
    
    def register(self, login: str, email: str, password: str) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            login: Username.
            email: Email address.
            password: Password.
        
        Returns:
            Auth response with user info and token.
        """
        payload = {
            "login": login,
            "email": email,
            "password": password,
        }
        response = self.session.post(self._url("/auth/register"), json=payload)
        response.raise_for_status()
        return response.json()
    
    def login(self, login: str, password: str) -> Dict[str, Any]:
        """
        Login with credentials.
        
        Args:
            login: Username or email.
            password: Password.
        
        Returns:
            Auth response with user info and token.
        """
        payload = {
            "login": login,
            "password": password,
        }
        response = self.session.post(self._url("/auth/login"), json=payload)
        response.raise_for_status()
        return response.json()
    
    def logout(self, token: str) -> Dict[str, Any]:
        """
        Logout user.
        
        Args:
            token: Access token.
        
        Returns:
            Logout confirmation.
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.post(self._url("/auth/logout"), headers=headers)
        response.raise_for_status()
        return response.json()
    
    def get_current_user(self, token: str) -> Dict[str, Any]:
        """
        Get current user info.
        
        Args:
            token: Access token.
        
        Returns:
            User information.
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(self._url("/auth/me"), headers=headers)
        response.raise_for_status()
        return response.json()
    
    def create_rating(
        self, spot_id: int, nota: int, comentario: Optional[str], token: str
    ) -> Dict[str, Any]:
        """
        Create a rating for a spot.
        
        Args:
            spot_id: Spot ID.
            nota: Rating value (1-5).
            comentario: Optional review comment.
            token: Access token.
        
        Returns:
            Created rating.
        """
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"nota": nota}
        if comentario:
            payload["comentario"] = comentario
        
        response = self.session.post(
            self._url(f"/spots/{spot_id}/ratings"),
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def update_rating(
        self, rating_id: int, nota: Optional[int], comentario: Optional[str], token: str
    ) -> Dict[str, Any]:
        """
        Update a rating.
        
        Args:
            rating_id: Rating ID.
            nota: New rating value (1-5).
            comentario: New review comment.
            token: Access token.
        
        Returns:
            Updated rating.
        """
        headers = {"Authorization": f"Bearer {token}"}
        payload = {}
        if nota is not None:
            payload["nota"] = nota
        if comentario is not None:
            payload["comentario"] = comentario
        
        response = self.session.put(
            self._url(f"/ratings/{rating_id}"),
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_spot_comments(
        self,
        spot_id: int,
        page: int = 1,
        per_page: int = 20,
        ordenacao: str = "recentes"
    ) -> Dict[str, Any]:
        """
        Get comments for a spot.
        
        Args:
            spot_id: Spot ID.
            page: Page number.
            per_page: Items per page.
            ordenacao: Sort order (recentes, antigas, mais_curtidos).
        
        Returns:
            Comments list with pagination.
        """
        params = {
            "page": page,
            "per_page": per_page,
            "ordenacao": ordenacao
        }
        response = self.session.get(
            self._url(f"/spots/{spot_id}/comments"),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def create_comment(
        self, spot_id: int, texto: str, token: str
    ) -> Dict[str, Any]:
        """
        Create a comment for a spot.
        
        Args:
            spot_id: Spot ID.
            texto: Comment text.
            token: Access token.
        
        Returns:
            Created comment.
        """
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"texto": texto}
        
        response = self.session.post(
            self._url(f"/spots/{spot_id}/comments"),
            json=payload,
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def like_comment(self, comment_id: str) -> None:
        """
        Like a comment.
        
        Args:
            comment_id: Comment ID.
        """
        response = self.session.post(self._url(f"/comments/{comment_id}/like"))
        response.raise_for_status()
    
    def report_comment(self, comment_id: str) -> None:
        """
        Report a comment for moderation.
        
        Args:
            comment_id: Comment ID.
        """
        response = self.session.post(self._url(f"/comments/{comment_id}/report"))
        response.raise_for_status()
    
    # Accommodation methods
    def get_spot_accommodations(
        self,
        spot_id: int,
        tipo: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get accommodations for a spot.
        
        Args:
            spot_id: Spot ID.
            tipo: Filter by type (hotel, pousada, hostel).
            min_price: Minimum price filter.
            max_price: Maximum price filter.
        
        Returns:
            Accommodations list with total count.
        """
        params = {}
        if tipo:
            params["tipo"] = tipo
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price
        
        response = self.session.get(
            self._url(f"/spots/{spot_id}/accommodations"),
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_accommodation_statistics(self, spot_id: int) -> Dict[str, Any]:
        """
        Get accommodation statistics for a spot.
        
        Args:
            spot_id: Spot ID.
        
        Returns:
            Statistics dictionary.
        """
        response = self.session.get(
            self._url(f"/spots/{spot_id}/accommodations/statistics")
        )
        response.raise_for_status()
        return response.json()
    
    def get_accommodation(self, accommodation_id: int) -> Dict[str, Any]:
        """
        Get accommodation by ID.
        
        Args:
            accommodation_id: Accommodation ID.
        
        Returns:
            Accommodation details.
        """
        response = self.session.get(
            self._url(f"/accommodations/{accommodation_id}")
        )
        response.raise_for_status()
        return response.json()
    
    def delete_accommodation(self, accommodation_id: int, token: str) -> None:
        """
        Delete an accommodation (admin only).
        
        Args:
            accommodation_id: Accommodation ID.
            token: Admin access token.
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.delete(
            self._url(f"/accommodations/{accommodation_id}"),
            headers=headers
        )
        response.raise_for_status()
    
    # Favorites methods
    def get_my_favorites(self, token: str) -> List[Dict[str, Any]]:
        """
        Get authenticated user's favorites.
        
        Args:
            token: Access token.
        
        Returns:
            List of favorites with spot details.
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(
            self._url("/favorites"),
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def add_favorite(self, spot_id: int, token: str) -> Dict[str, Any]:
        """
        Add spot to favorites.
        
        Args:
            spot_id: Spot ID.
            token: Access token.
        
        Returns:
            Created favorite information.
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.post(
            self._url(f"/spots/{spot_id}/favorite"),
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def remove_favorite(self, spot_id: int, token: str) -> None:
        """
        Remove spot from favorites.
        
        Args:
            spot_id: Spot ID.
            token: Access token.
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.delete(
            self._url(f"/spots/{spot_id}/favorite"),
            headers=headers
        )
        response.raise_for_status()
    
    def toggle_favorite(self, spot_id: int, token: str) -> Dict[str, Any]:
        """
        Toggle favorite status for a spot.
        
        Args:
            spot_id: Spot ID.
            token: Access token.
        
        Returns:
            Action taken and new status.
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.post(
            self._url(f"/spots/{spot_id}/favorite/toggle"),
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    
    def check_favorite_status(self, spot_id: int, token: str) -> bool:
        """
        Check if spot is in user's favorites.
        
        Args:
            spot_id: Spot ID.
            token: Access token.
        
        Returns:
            True if favorited, False otherwise.
        """
        headers = {"Authorization": f"Bearer {token}"}
        response = self.session.get(
            self._url(f"/spots/{spot_id}/favorite/status"),
            headers=headers
        )
        response.raise_for_status()
        return response.json().get("is_favorited", False)
