"""
日期時間工具函數
"""
from datetime import datetime, timezone


def get_utc_now() -> str:
    """
    生成 UTC 時間並加上 'Z' 後綴，讓前端正確識別為 UTC 時間
    
    Returns:
        ISO 格式的 UTC 時間字符串，例如：'2026-02-06T08:17:40.053Z'
    """
    return datetime.utcnow().replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')


def safe_parse_iso_datetime(s: str) -> datetime:
    """
    安全解析 ISO 格式的日期時間字符串（兼容 Python 3.9）
    
    Args:
        s: ISO 格式的日期時間字符串
        
    Returns:
        datetime 對象（帶時區信息）
    """
    # Python 3.9 的 fromisoformat 不支援 'Z' 後綴，需要先替換
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        # 如果還是失敗，嘗試使用 strptime
        try:
            dt = datetime.strptime(s.replace('Z', ''), '%Y-%m-%dT%H:%M:%S.%f')
            dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            # 嘗試沒有微秒的格式
            dt = datetime.strptime(s.replace('Z', ''), '%Y-%m-%dT%H:%M:%S')
            dt = dt.replace(tzinfo=timezone.utc)
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt
