"""
Redis 連接管理
"""
import redis
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

# 創建 Redis 客戶端
try:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True
    )
    # 測試連接
    redis_client.ping()
    logger.info(f"Redis 連接成功: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
except Exception as e:
    logger.error(f"Redis 連接失敗: {e}")
    raise
