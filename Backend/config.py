"""
應用程式配置管理
使用環境變數和預設值來管理配置
"""
import os
from typing import List


class Settings:
    """應用程式設定"""
    
    # 應用程式設定
    APP_NAME: str = os.getenv("APP_NAME", "SyncNote API")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Redis 配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_KEY_PREFIX: str = os.getenv("REDIS_KEY_PREFIX", "note:")
    
    # MongoDB 配置
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DB_NAME: str = os.getenv("DB_NAME", "note_db")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "notes")
    
    # Socket.IO 配置
    SOCKETIO_PATH: str = os.getenv("SOCKETIO_PATH", "/ws/socket.io")
    SOCKETIO_CORS_ORIGINS: str = os.getenv("SOCKETIO_CORS_ORIGINS", "*")
    
    # CORS 配置
    _CORS_ORIGINS_STR: str = os.getenv("CORS_ORIGINS", "*")
    CORS_CREDENTIALS: bool = os.getenv("CORS_CREDENTIALS", "True").lower() == "true"
    CORS_METHODS: List[str] = os.getenv("CORS_METHODS", "*").split(",") if os.getenv("CORS_METHODS") != "*" else ["*"]
    CORS_HEADERS: List[str] = os.getenv("CORS_HEADERS", "*").split(",") if os.getenv("CORS_HEADERS") != "*" else ["*"]
    
    # 日誌配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """處理 CORS_ORIGINS，支援 '*' 或逗號分隔的字符串"""
        if self._CORS_ORIGINS_STR == "*":
            return ["*"]
        return [origin.strip() for origin in self._CORS_ORIGINS_STR.split(",")]


# 創建全局設定實例
settings = Settings()

# 處理 SOCKETIO_CORS_ORIGINS
if settings.SOCKETIO_CORS_ORIGINS == "*":
    socketio_cors_origins = "*"
else:
    socketio_cors_origins = [origin.strip() for origin in settings.SOCKETIO_CORS_ORIGINS.split(",")]
