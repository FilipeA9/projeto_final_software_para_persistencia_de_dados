"""
Import Utilities - Import tourist spot data from CSV and JSON formats.

Provides functions to parse and validate imported data.
"""

import csv
import json
from typing import List, Dict, Any, Tuple
from io import StringIO


class ImportService:
    """Service for importing tourist spot data."""

    @staticmethod
    def validate_spot_data(spot: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a spot dictionary for required fields and formats.
        
        Args:
            spot: Spot dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Required fields
        required_fields = ["nome", "cidade", "estado", "pais", "latitude", "longitude"]
        for field in required_fields:
            if field not in spot or spot[field] is None or spot[field] == "":
                errors.append(f"Missing required field: {field}")
        
        # Validate latitude
        if "latitude" in spot:
            try:
                lat = float(spot["latitude"])
                if not (-90 <= lat <= 90):
                    errors.append(f"Latitude must be between -90 and 90, got: {lat}")
            except (ValueError, TypeError):
                errors.append(f"Invalid latitude value: {spot['latitude']}")
        
        # Validate longitude
        if "longitude" in spot:
            try:
                lon = float(spot["longitude"])
                if not (-180 <= lon <= 180):
                    errors.append(f"Longitude must be between -180 and 180, got: {lon}")
            except (ValueError, TypeError):
                errors.append(f"Invalid longitude value: {spot['longitude']}")
        
        # Validate nome length
        if "nome" in spot and len(str(spot["nome"])) > 200:
            errors.append("Nome must be 200 characters or less")
        
        # Validate descricao length
        if "descricao" in spot and spot["descricao"] and len(str(spot["descricao"])) > 2000:
            errors.append("Descricao must be 2000 characters or less")
        
        return len(errors) == 0, errors

    @staticmethod
    def parse_json(json_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parse JSON content and extract spot data.
        
        Args:
            json_content: JSON string
            
        Returns:
            Tuple of (list_of_spots, list_of_errors)
        """
        errors = []
        spots = []
        
        try:
            data = json.loads(json_content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                spots = data
            elif isinstance(data, dict):
                if "data" in data:
                    spots = data["data"]
                elif "spots" in data:
                    spots = data["spots"]
                else:
                    # Try to treat the dict as a single spot
                    spots = [data]
            else:
                errors.append("Invalid JSON structure: expected list or object")
                return [], errors
            
            # Validate each spot
            valid_spots = []
            for idx, spot in enumerate(spots):
                is_valid, spot_errors = ImportService.validate_spot_data(spot)
                if is_valid:
                    valid_spots.append(spot)
                else:
                    for error in spot_errors:
                        errors.append(f"Spot {idx + 1}: {error}")
            
            return valid_spots, errors
            
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON format: {str(e)}")
            return [], errors
        except Exception as e:
            errors.append(f"Error parsing JSON: {str(e)}")
            return [], errors

    @staticmethod
    def parse_csv(csv_content: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parse CSV content and extract spot data.
        
        Args:
            csv_content: CSV string
            
        Returns:
            Tuple of (list_of_spots, list_of_errors)
        """
        errors = []
        spots = []
        
        try:
            # Read CSV
            csv_file = StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            # Parse each row
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (1 is header)
                spot = {}
                
                # Map CSV fields to spot fields
                field_mapping = {
                    "id": "id",
                    "nome": "nome",
                    "descricao": "descricao",
                    "cidade": "cidade",
                    "estado": "estado",
                    "pais": "pais",
                    "latitude": "latitude",
                    "longitude": "longitude",
                    "endereco": "endereco",
                }
                
                for csv_field, spot_field in field_mapping.items():
                    if csv_field in row:
                        value = row[csv_field].strip() if row[csv_field] else None
                        if value:
                            spot[spot_field] = value
                
                # Convert numeric fields
                if "latitude" in spot:
                    try:
                        spot["latitude"] = float(spot["latitude"])
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid latitude value")
                        continue
                
                if "longitude" in spot:
                    try:
                        spot["longitude"] = float(spot["longitude"])
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid longitude value")
                        continue
                
                # Validate spot
                is_valid, spot_errors = ImportService.validate_spot_data(spot)
                if is_valid:
                    spots.append(spot)
                else:
                    for error in spot_errors:
                        errors.append(f"Row {row_num}: {error}")
            
            return spots, errors
            
        except Exception as e:
            errors.append(f"Error parsing CSV: {str(e)}")
            return [], errors

    @staticmethod
    def import_spots(
        content: str,
        format: str,
    ) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
        """
        Import spots from content string.
        
        Args:
            content: File content as string
            format: Format type ("json" or "csv")
            
        Returns:
            Tuple of (valid_spots, errors, summary)
            
        Raises:
            ValueError: If format is not supported
        """
        if format.lower() == "json":
            spots, errors = ImportService.parse_json(content)
        elif format.lower() == "csv":
            spots, errors = ImportService.parse_csv(content)
        else:
            raise ValueError(f"Unsupported import format: {format}")
        
        summary = {
            "total_records": len(spots) + len(errors),
            "valid_records": len(spots),
            "invalid_records": len(errors),
            "format": format,
        }
        
        return spots, errors, summary

    @staticmethod
    def prepare_spot_for_db(spot: Dict[str, Any], creator_id: int) -> Dict[str, Any]:
        """
        Prepare a spot dictionary for database insertion.
        
        Args:
            spot: Validated spot dictionary
            creator_id: User ID of the creator
            
        Returns:
            Database-ready spot dictionary
        """
        db_spot = {
            "nome": spot["nome"],
            "descricao": spot.get("descricao", ""),
            "cidade": spot["cidade"],
            "estado": spot["estado"],
            "pais": spot["pais"],
            "latitude": float(spot["latitude"]),
            "longitude": float(spot["longitude"]),
            "endereco": spot.get("endereco", ""),
            "criado_por": creator_id,
        }
        
        return db_spot
