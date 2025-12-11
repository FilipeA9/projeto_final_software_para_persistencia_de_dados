"""
Directions Service - Provides location and directions information for tourist spots.

This service handles coordinate validation and directions generation for tourist spots.
It can be extended to integrate with external maps APIs (Google Maps, OpenStreetMap, etc.)
"""

from typing import Dict, Any, Optional, Tuple
from math import radians, sin, cos, sqrt, atan2


class DirectionsService:
    """Service for generating directions and location information."""

    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """
        Validate geographic coordinates.
        
        Args:
            latitude: Latitude value (-90 to 90)
            longitude: Longitude value (-180 to 180)
            
        Returns:
            True if coordinates are valid, False otherwise
        """
        return -90 <= latitude <= 90 and -180 <= longitude <= 180

    @staticmethod
    def calculate_distance(
        lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        Calculate distance between two points using Haversine formula.
        
        Args:
            lat1: Latitude of first point
            lon1: Longitude of first point
            lat2: Latitude of second point
            lon2: Longitude of second point
            
        Returns:
            Distance in kilometers
        """
        # Earth's radius in kilometers
        R = 6371.0

        # Convert degrees to radians
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        # Haversine formula
        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return round(distance, 2)

    @staticmethod
    def get_directions_info(
        spot_id: int,
        spot_name: str,
        latitude: float,
        longitude: float,
        address: str,
        cidade: str,
        estado: str,
        pais: str,
        from_latitude: Optional[float] = None,
        from_longitude: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Get directions information for a tourist spot.
        
        Args:
            spot_id: ID of the tourist spot
            spot_name: Name of the tourist spot
            latitude: Spot latitude
            longitude: Spot longitude
            address: Spot address
            cidade: City name
            estado: State name
            pais: Country name
            from_latitude: Starting point latitude (optional)
            from_longitude: Starting point longitude (optional)
            
        Returns:
            Dictionary with directions information
        """
        # Validate spot coordinates
        if not DirectionsService.validate_coordinates(latitude, longitude):
            raise ValueError("Invalid spot coordinates")

        # Base information
        directions_info = {
            "spotId": spot_id,
            "spotName": spot_name,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "location": {
                "address": address,
                "city": cidade,
                "state": estado,
                "country": pais,
            },
            "googleMapsUrl": f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}",
            "googleMapsDirectionsUrl": f"https://www.google.com/maps/dir/?api=1&destination={latitude},{longitude}",
        }

        # If starting point provided, calculate distance
        if from_latitude is not None and from_longitude is not None:
            if DirectionsService.validate_coordinates(from_latitude, from_longitude):
                distance = DirectionsService.calculate_distance(
                    from_latitude, from_longitude, latitude, longitude
                )
                directions_info["distance"] = {
                    "value": distance,
                    "unit": "km",
                    "text": f"{distance} km",
                }
                directions_info["from"] = {
                    "latitude": from_latitude,
                    "longitude": from_longitude,
                }
                directions_info["googleMapsDirectionsUrl"] = (
                    f"https://www.google.com/maps/dir/?api=1"
                    f"&origin={from_latitude},{from_longitude}"
                    f"&destination={latitude},{longitude}"
                )

        # Text-based directions
        directions_info["textDirections"] = [
            f"Navigate to {spot_name} located in {cidade}, {estado}, {pais}",
            f"Address: {address}",
            f"Coordinates: {latitude}, {longitude}",
            "Open Google Maps for detailed turn-by-turn directions",
        ]

        return directions_info

    @staticmethod
    def get_nearby_spots_info(
        spots: list,
        reference_latitude: float,
        reference_longitude: float,
        max_distance_km: float = 50.0,
    ) -> list:
        """
        Get information about nearby spots relative to a reference point.
        
        Args:
            spots: List of spot dictionaries with coordinates
            reference_latitude: Reference point latitude
            reference_longitude: Reference point longitude
            max_distance_km: Maximum distance to consider (default 50km)
            
        Returns:
            List of spots with distance information, sorted by distance
        """
        if not DirectionsService.validate_coordinates(
            reference_latitude, reference_longitude
        ):
            raise ValueError("Invalid reference coordinates")

        nearby_spots = []

        for spot in spots:
            spot_lat = spot.get("latitude")
            spot_lon = spot.get("longitude")

            if spot_lat is None or spot_lon is None:
                continue

            if not DirectionsService.validate_coordinates(spot_lat, spot_lon):
                continue

            distance = DirectionsService.calculate_distance(
                reference_latitude, reference_longitude, spot_lat, spot_lon
            )

            if distance <= max_distance_km:
                spot_info = spot.copy()
                spot_info["distance"] = {
                    "value": distance,
                    "unit": "km",
                    "text": f"{distance} km",
                }
                nearby_spots.append(spot_info)

        # Sort by distance
        nearby_spots.sort(key=lambda x: x["distance"]["value"])

        return nearby_spots
