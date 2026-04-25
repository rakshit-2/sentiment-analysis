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


def connect_to_mongo_sync():
    """
    Establish connection to MongoDB (synchronous version for Celery workers).
    Called during Celery worker startup.
    """
    global _client, _database
    
    try:
        logger.info("Connecting to MongoDB (sync)...")
        
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
        
        # Create indexes if needed (synchronously)
        create_indexes_sync()
        
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


def close_mongo_connection_sync():
    """
    Close MongoDB connection (synchronous version for Celery workers).
    """
    global _client, _database
    
    if _client:
        logger.info("Closing MongoDB connection (sync)...")
        _client.close()
        _client = None
        _database = None
        logger.info("✅ MongoDB connection closed")


async def create_indexes():
    """Create database indexes for better query performance."""
    try:
        db = get_database()
        
        # Transcripts collection indexes
        db.transcripts.create_index("uuid", unique=True)
        logger.info("✅ Created unique index on transcripts.uuid")
        
        db.transcripts.create_index("source")
        logger.info("✅ Created index on transcripts.source")
        
        db.transcripts.create_index("is_deleted")
        logger.info("✅ Created index on transcripts.is_deleted")
        
        db.transcripts.create_index([("created_at", -1)])
        logger.info("✅ Created descending index on transcripts.created_at")
        
        # Analyses collection indexes
        db.analyses.create_index("uuid", unique=True)
        logger.info("✅ Created unique index on analyses.uuid")
        
        db.analyses.create_index("transcript_id")
        logger.info("✅ Created index on analyses.transcript_id")
        
        db.analyses.create_index("status")
        logger.info("✅ Created index on analyses.status")
        
        db.analyses.create_index("is_deleted")
        logger.info("✅ Created index on analyses.is_deleted")
        
        db.analyses.create_index([("created_at", -1)])
        logger.info("✅ Created descending index on analyses.created_at")
        
    except Exception as e:
        logger.warning(f"⚠️ Error creating indexes: {str(e)}")


def create_indexes_sync():
    """Create database indexes for better query performance (synchronous version)."""
    try:
        db = get_database()
        
        # Transcripts collection indexes
        db.transcripts.create_index("uuid", unique=True)
        logger.info("✅ Created unique index on transcripts.uuid")
        
        db.transcripts.create_index("source")
        logger.info("✅ Created index on transcripts.source")
        
        db.transcripts.create_index("is_deleted")
        logger.info("✅ Created index on transcripts.is_deleted")
        
        db.transcripts.create_index([("created_at", -1)])
        logger.info("✅ Created descending index on transcripts.created_at")
        
        # Analyses collection indexes
        db.analyses.create_index("uuid", unique=True)
        logger.info("✅ Created unique index on analyses.uuid")
        
        db.analyses.create_index("transcript_id")
        logger.info("✅ Created index on analyses.transcript_id")
        
        db.analyses.create_index("status")
        logger.info("✅ Created index on analyses.status")
        
        db.analyses.create_index("is_deleted")
        logger.info("✅ Created index on analyses.is_deleted")
        
        db.analyses.create_index([("created_at", -1)])
        logger.info("✅ Created descending index on analyses.created_at")
        
    except Exception as e:
        logger.warning(f"⚠️ Error creating indexes: {str(e)}")


# Collection accessors
def get_transcripts_collection():
    """Get the transcripts collection."""
    return get_database().transcripts


def get_analyses_collection():
    """Get the analyses collection."""
    return get_database().analyses
