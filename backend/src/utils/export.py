"""
Export Utilities - Export tourist spot data to CSV and JSON formats.

Provides functions to export tourist spots with related data.
"""

import csv
import json
from typing import List, Dict, Any
from datetime import datetime
from io import StringIO


class ExportService:
    """Service for exporting tourist spot data."""

    @staticmethod
    def export_to_json(spots: List[Dict[str, Any]], include_metadata: bool = True) -> str:
        """
        Export tourist spots to JSON format.
        
        Args:
            spots: List of spot dictionaries
            include_metadata: Whether to include export metadata
            
        Returns:
            JSON string
        """
        export_data = {
            "data": spots,
        }
        
        if include_metadata:
            export_data["metadata"] = {
                "exported_at": datetime.utcnow().isoformat(),
                "total_spots": len(spots),
                "format_version": "1.0",
            }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)

    @staticmethod
    def export_to_csv(spots: List[Dict[str, Any]]) -> str:
        """
        Export tourist spots to CSV format.
        
        Args:
            spots: List of spot dictionaries
            
        Returns:
            CSV string
        """
        if not spots:
            return ""
        
        output = StringIO()
        
        # Define CSV columns
        fieldnames = [
            "id",
            "nome",
            "descricao",
            "cidade",
            "estado",
            "pais",
            "latitude",
            "longitude",
            "endereco",
            "criado_por",
            "created_at",
            "avg_rating",
            "rating_count",
            "photo_count",
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for spot in spots:
            # Flatten the spot data for CSV
            row = {
                "id": spot.get("id"),
                "nome": spot.get("nome"),
                "descricao": spot.get("descricao"),
                "cidade": spot.get("cidade"),
                "estado": spot.get("estado"),
                "pais": spot.get("pais"),
                "latitude": spot.get("latitude"),
                "longitude": spot.get("longitude"),
                "endereco": spot.get("endereco"),
                "criado_por": spot.get("criado_por"),
                "created_at": spot.get("created_at"),
                "avg_rating": spot.get("avg_rating"),
                "rating_count": spot.get("rating_count"),
                "photo_count": spot.get("photo_count", 0),
            }
            writer.writerow(row)
        
        return output.getvalue()

    @staticmethod
    def prepare_spot_for_export(spot_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a spot dictionary for export by formatting dates and types.
        
        Args:
            spot_dict: Raw spot dictionary
            
        Returns:
            Formatted spot dictionary
        """
        export_spot = spot_dict.copy()
        
        # Format datetime fields
        if "created_at" in export_spot and isinstance(export_spot["created_at"], datetime):
            export_spot["created_at"] = export_spot["created_at"].isoformat()
        
        # Convert Decimal to float for latitude/longitude
        if "latitude" in export_spot:
            export_spot["latitude"] = float(export_spot["latitude"])
        if "longitude" in export_spot:
            export_spot["longitude"] = float(export_spot["longitude"])
        
        # Round avg_rating
        if "avg_rating" in export_spot and export_spot["avg_rating"] is not None:
            export_spot["avg_rating"] = round(float(export_spot["avg_rating"]), 2)
        
        return export_spot

    @staticmethod
    def export_spots_with_details(
        spots: List[Dict[str, Any]],
        format: str = "json",
        include_metadata: bool = True,
    ) -> str:
        """
        Export spots with formatting and metadata.
        
        Args:
            spots: List of spot dictionaries
            format: Export format ("json" or "csv")
            include_metadata: Whether to include export metadata (JSON only)
            
        Returns:
            Formatted export string
            
        Raises:
            ValueError: If format is not supported
        """
        # Prepare all spots for export
        prepared_spots = [
            ExportService.prepare_spot_for_export(spot) for spot in spots
        ]
        
        if format.lower() == "json":
            return ExportService.export_to_json(prepared_spots, include_metadata)
        elif format.lower() == "csv":
            return ExportService.export_to_csv(prepared_spots)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    @staticmethod
    def get_export_filename(format: str, prefix: str = "turistando_spots") -> str:
        """
        Generate a filename for export.
        
        Args:
            format: File format ("json" or "csv")
            prefix: Filename prefix
            
        Returns:
            Generated filename with timestamp
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}.{format.lower()}"
