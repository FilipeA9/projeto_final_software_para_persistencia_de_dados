"""
MongoDB database connection and client management.

Provides async Motor client for MongoDB operations.
"""

from typing import AsyncGenerator, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure

from src.config.settings import settings

# Global MongoDB client
_mongo_client: AsyncIOMotorClient | None = None
_mongo_db: AsyncIOMotorDatabase | None = None


def get_mongo_client() -> AsyncIOMotorClient:
    """
    Get MongoDB client instance.
    
    Returns:
        AsyncIOMotorClient: MongoDB client for async operations.
    """
    global _mongo_client
    if _mongo_client is None:
        # Add authSource parameter for MongoDB authentication
        mongo_url = settings.MONGODB_URL
        if "authSource" not in mongo_url:
            if "?" in mongo_url:
                mongo_url += "&authSource=admin"
            else:
                mongo_url += "?authSource=admin"
        
        _mongo_client = AsyncIOMotorClient(
            mongo_url,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
        )
    return _mongo_client


def get_mongo_db() -> AsyncIOMotorDatabase:
    """
    Get MongoDB database instance.
    
    Returns:
        AsyncIOMotorDatabase: Database instance for collections.
    """
    global _mongo_db
    if _mongo_db is None:
        client = get_mongo_client()
        _mongo_db = client[settings.MONGODB_DATABASE]
    return _mongo_db


async def init_mongo() -> None:
    """
    Initialize MongoDB connection and create collections with validation.
    
    Creates comentarios and fotos collections with schema validation.
    """
    db = get_mongo_db()
    
    # Test connection
    try:
        await db.command("ping")
        print("MongoDB connection established successfully")
    except ConnectionFailure as e:
        print(f"MongoDB connection failed: {e}")
        raise
    
    # Get existing collections
    existing_collections = await db.list_collection_names()
    
    # Create comentarios collection with validation
    if "comentarios" not in existing_collections:
        await db.create_collection(
            "comentarios",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["pontoId", "usuarioId", "texto", "createdAt"],
                    "properties": {
                        "pontoId": {"bsonType": "int"},
                        "usuarioId": {"bsonType": "int"},
                        "texto": {"bsonType": "string", "maxLength": 500},
                        "createdAt": {"bsonType": "date"},
                        "metadata": {
                            "bsonType": "object",
                            "properties": {
                                "likes": {"bsonType": "int"},
                                "reports": {"bsonType": "int"},
                            },
                        },
                        "respostas": {
                            "bsonType": "array",
                            "items": {
                                "bsonType": "object",
                                "required": ["usuarioId", "texto", "createdAt"],
                                "properties": {
                                    "usuarioId": {"bsonType": "int"},
                                    "texto": {"bsonType": "string", "maxLength": 500},
                                    "createdAt": {"bsonType": "date"},
                                },
                            },
                        },
                    },
                }
            },
        )
        # Create indexes for comentarios
        await db.comentarios.create_index("pontoId")
        await db.comentarios.create_index("usuarioId")
        await db.comentarios.create_index([("createdAt", -1)])
        print("Created comentarios collection with validation")
    
    # Create fotos collection with validation
    if "fotos" not in existing_collections:
        await db.create_collection(
            "fotos",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["pontoId", "usuarioId", "filename", "path", "createdAt"],
                    "properties": {
                        "pontoId": {"bsonType": "int"},
                        "usuarioId": {"bsonType": "int"},
                        "filename": {"bsonType": "string"},
                        "titulo": {"bsonType": "string", "maxLength": 200},
                        "path": {"bsonType": "string"},
                        "thumbnailPath": {"bsonType": "string"},
                        "createdAt": {"bsonType": "date"},
                    },
                }
            },
        )
        # Create indexes for fotos
        await db.fotos.create_index("pontoId")
        await db.fotos.create_index("usuarioId")
        await db.fotos.create_index([("createdAt", -1)])
        print("Created fotos collection with validation")


async def close_mongo() -> None:
    """Close MongoDB connection and cleanup resources."""
    global _mongo_client, _mongo_db
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None
        print("MongoDB connection closed")
