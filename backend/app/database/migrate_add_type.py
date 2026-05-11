"""
Database migration script to add 'type' field to existing transcripts.
Sets all existing transcripts to 'voice' type for backward compatibility.
"""
import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import connect_to_mongo, close_mongo_connection, get_database
from models.transcript import TranscriptType

async def migrate_add_transcript_type():
    """Add type field to all existing transcripts."""
    # Initialize database connection
    await connect_to_mongo()
    
    db = get_database()  # get_database() is not async
    transcripts_collection = db["transcripts"]
    
    # Count documents without type field (PyMongo methods are synchronous)
    count_without_type = transcripts_collection.count_documents({"type": {"$exists": False}})
    
    print(f"Found {count_without_type} transcripts without 'type' field")
    
    if count_without_type == 0:
        print("✅ No migration needed - all transcripts already have 'type' field")
        return
    
    # Update all transcripts without type field to default 'voice'
    result = transcripts_collection.update_many(
        {"type": {"$exists": False}},
        {"$set": {"type": TranscriptType.VOICE.value}}
    )
    
    print(f"✅ Migration completed: Updated {result.modified_count} transcripts to type='voice'")
    
    # Verify
    count_voice = transcripts_collection.count_documents({"type": TranscriptType.VOICE.value})
    count_digital = transcripts_collection.count_documents({"type": TranscriptType.DIGITAL.value})
    
    print(f"\n📊 Current transcript counts:")
    print(f"   Voice transcripts: {count_voice}")
    print(f"   Digital transcripts: {count_digital}")
    print(f"   Total: {count_voice + count_digital}")


async def run_migration():
    """Run migration with proper connection handling."""
    try:
        await migrate_add_transcript_type()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    print("🔄 Starting transcript type migration...")
    asyncio.run(run_migration())
    print("\n✅ Migration completed successfully!")
