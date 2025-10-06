from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

def get_database() -> AsyncIOMotorDatabase:
    return Database.db

async def connect_to_mongo():
    logger.info("Connecting to MongoDB...")
    Database.client = AsyncIOMotorClient(settings.mongo_url)
    Database.db = Database.client[settings.db_name]
    logger.info(f"Connected to MongoDB: {settings.db_name}")

async def close_mongo_connection():
    logger.info("Closing MongoDB connection...")
    Database.client.close()
    logger.info("MongoDB connection closed")
