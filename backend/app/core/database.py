from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
from app.core.firestore_adapter import FirestoreDB
from app.core.firebase import initialize_firebase
import logging

logger = logging.getLogger(__name__)

class Database:
    # MongoDB (kept as backup)
    mongo_client: AsyncIOMotorClient = None
    mongo_db: AsyncIOMotorDatabase = None
    
    # Firestore (primary database)
    firestore_db: FirestoreDB = None
    use_firestore: bool = True  # Switch to control which DB to use

def get_database():
    """Get the current database instance (Firestore or MongoDB)"""
    if Database.use_firestore:
        return Database.firestore_db
    else:
        return Database.mongo_db

async def connect_to_mongo():
    """Connect to MongoDB (kept as backup)"""
    logger.info("Connecting to MongoDB (backup)...")
    Database.mongo_client = AsyncIOMotorClient(settings.mongo_url)
    Database.mongo_db = Database.mongo_client[settings.db_name]
    logger.info(f"Connected to MongoDB: {settings.db_name}")

async def close_mongo_connection():
    """Close MongoDB connection"""
    if Database.mongo_client:
        logger.info("Closing MongoDB connection...")
        Database.mongo_client.close()
        logger.info("MongoDB connection closed")

def connect_to_firestore():
    """Initialize Firestore connection"""
    logger.info("Connecting to Firestore...")
    try:
        initialize_firebase()
        Database.firestore_db = FirestoreDB()
        logger.info("✅ Connected to Firestore successfully")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Firestore: {str(e)}")
        logger.info("Falling back to MongoDB...")
        Database.use_firestore = False
        raise
