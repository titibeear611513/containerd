"""
Redis 工具函數
"""
from config import settings


def get_redis_key(note_id: str) -> str:
    """
    生成 Redis key
    
    Args:
        note_id: 筆記 ID
        
    Returns:
        Redis key，例如：'note:12345'
    """
    return f"{settings.REDIS_KEY_PREFIX}{note_id}"
