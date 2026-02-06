"""
日誌系統配置
"""
import logging
import sys
from config import settings

# 配置日誌格式
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 配置日誌級別
LOG_LEVEL = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    設置並返回 logger 實例
    
    Args:
        name: logger 名稱，通常是模組名稱
        
    Returns:
        配置好的 logger 實例
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # 避免重複添加 handler
    if logger.handlers:
        return logger
    
    # 創建 console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    
    # 創建格式器
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(formatter)
    
    # 添加 handler
    logger.addHandler(console_handler)
    
    return logger


# 創建全局 logger
logger = setup_logger("SyncNote")
