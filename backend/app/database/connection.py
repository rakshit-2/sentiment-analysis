from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional
import logging

from app.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Global MongoDB client and database instances
_client: Optional[MongoClient] = None
_database = None


def get_database():
    """Get the MongoDB database instance."""
    global _database
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return _database


def get_client():
    """Get the MongoDB client instance."""
    global _client
    if _client is None:
        raise RuntimeError("Database client not initialized. Call connect_to_mongo() first.")
    return _client


async def connect_to_mongo():
    """
    Establish connection to MongoDB.
    Called during application startup.
    """
    global _client, _database
    
    try:
        logger.info("Connecting to MongoDB...")
        
        # Create MongoDB client
        _client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Verify connection by pinging the database
        _client.admin.command('ping')
        
        # Get database instance
        _database = _client[settings.mongodb_database]
        
        logger.info(f"✅ Successfully connected to MongoDB database: {settings.mongodb_database}")
        
        # Create indexes if needed
        await create_indexes()
        
        return _database
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"❌ Failed to connect to MongoDB: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error during MongoDB connection: {str(e)}")
        raise


async def close_mongo_connection():
    """
    Close MongoDB connection.
    Called during application shutdown.
    """
    global _client, _database
    
    if _client:
        logger.info("Closing MongoDB connection...")
        _client.close()
        _client = None
        _database = None
        logger.info("✅ MongoDB connection closed")


async def create_indexes():
    """Create database indexes for better query performance."""
    try:
        db = get_database()
        
        # Create index on transcript_id in transcripts collection
        db.transcripts.create_index("transcript_id", unique=True)
        logger.info("✅ Created index on transcripts.transcript_id")
        
        # Create index on analysis_id in analyses collection
        db.analyses.create_index("analysis_id", unique=True)
        logger.info("✅ Created index on analyses.analysis_id")
        
        # Create index on transcript_id in analyses collection for foreign key lookups
        db.analyses.create_index("transcript_id")
        logger.info("✅ Created index on analyses.transcript_id")
        
    except Exception as e:
        logger.warning(f"⚠️ Error creating indexes: {str(e)}")


# Collection accessors
def get_transcripts_collection():
    """Get the transcripts collection."""
    return get_database().transcripts


def get_analyses_collection():
    """Get the analyses collection."""
    return get_database().analyses
