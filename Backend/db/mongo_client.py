"""
MongoDB 連接管理
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# 創建 MongoDB 客戶端
mongo_client = AsyncIOMotorClient(settings.MONGODB_URI)
db: AsyncIOMotorDatabase = mongo_client[settings.DB_NAME]
notes_collection: AsyncIOMotorCollection = db[settings.COLLECTION_NAME]

logger.info(f"MongoDB 連接成功: {settings.MONGODB_URI}")
