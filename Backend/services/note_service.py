"""
筆記業務邏輯服務層
"""
import json
import uuid
from typing import List, Optional
from fastapi import HTTPException

from model.note import Note, NoteCreate
from db.redis_client import redis_client
from db.mongo_client import notes_collection
from utils.redis_utils import get_redis_key
from utils.datetime_utils import get_utc_now, safe_parse_iso_datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)


class NoteService:
    """筆記服務類"""
    
    @staticmethod
    async def create_note(note: NoteCreate) -> Note:
        """
        創建新筆記
        
        Args:
            note: 筆記創建請求
            
        Returns:
            創建好的筆記
        """
        note_id = str(uuid.uuid4())
        now = get_utc_now()
        note_data = {
            "id": note_id,
            "title": note.title,
            "content": "",
            "created_at": now,
            "updated_at": now
        }
        note_key = get_redis_key(note_id)
        
        try:
            # 1. 快取到 Redis
            redis_client.set(note_key, json.dumps(note_data, ensure_ascii=False))
            # 2. 寫入 MongoDB
            await notes_collection.insert_one(note_data)
            # 3. 從 MongoDB 讀取，確保返回正確的格式
            created_note = await notes_collection.find_one({"id": note_id}, {"_id": 0})
            logger.info(f"創建筆記成功: {note_id}")
            return created_note
        except Exception as e:
            logger.error(f"創建筆記失敗: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="創建筆記失敗")
    
    @staticmethod
    async def get_note(note_id: str) -> Note:
        """
        獲取單個筆記
        
        Args:
            note_id: 筆記 ID
            
        Returns:
            筆記資料
            
        Raises:
            HTTPException: 筆記不存在
        """
        note_key = get_redis_key(note_id)
        data = redis_client.get(note_key)
        
        if data:
            return json.loads(data)
        
        # 若 Redis 沒有 → 查 MongoDB
        note_data = await notes_collection.find_one({"id": note_id}, {"_id": 0})
        if note_data:
            # 同步到 Redis 快取
            redis_client.set(note_key, json.dumps(note_data, ensure_ascii=False))
            logger.debug(f"從 MongoDB fallback 獲取筆記: {note_id}")
            return note_data
        
        logger.warning(f"筆記不存在: {note_id}")
        raise HTTPException(status_code=404, detail="筆記不存在")
    
    @staticmethod
    async def list_notes() -> List[Note]:
        """
        獲取所有筆記列表
        
        Returns:
            筆記列表（按創建時間倒序）
        """
        notes = []
        keys = []
        
        # 從 Redis 獲取所有筆記
        from config import settings
        for key in redis_client.scan_iter(match=f"{settings.REDIS_KEY_PREFIX}*"):
            keys.append(key)
        
        if keys:
            for key in keys:
                raw = redis_client.get(key)
                if raw:
                    note = json.loads(raw)
                    notes.append(note)
        else:
            # 從 MongoDB fallback
            cursor = notes_collection.find({}, {"_id": 0})
            async for note in cursor:
                notes.append(note)
                redis_client.set(get_redis_key(note['id']), json.dumps(note, ensure_ascii=False))
            logger.debug("從 MongoDB fallback 獲取筆記列表")
        
        # 按創建時間排序
        notes.sort(key=lambda n: safe_parse_iso_datetime(n["created_at"]), reverse=True)
        return notes
    
    @staticmethod
    async def delete_note(note_id: str) -> dict:
        """
        刪除筆記
        
        Args:
            note_id: 筆記 ID
            
        Returns:
            刪除成功訊息
            
        Raises:
            HTTPException: 筆記不存在
        """
        note_key = get_redis_key(note_id)
        
        try:
            # 1. 刪除 Redis 快取
            redis_client.delete(note_key)
            # 2. 刪除 MongoDB 文件
            result = await notes_collection.delete_one({"id": note_id})
            if result.deleted_count == 0:
                logger.warning(f"刪除筆記失敗，筆記不存在: {note_id}")
                raise HTTPException(status_code=404, detail="筆記不存在")
            
            logger.info(f"刪除筆記成功: {note_id}")
            return {"message": "筆記已刪除"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"刪除筆記失敗: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="刪除筆記失敗")
    
    @staticmethod
    async def update_note_title(note_id: str, title: str) -> Note:
        """
        更新筆記標題
        
        Args:
            note_id: 筆記 ID
            title: 新標題
            
        Returns:
            更新後的筆記
            
        Raises:
            HTTPException: 筆記不存在或更新失敗
        """
        note_key = get_redis_key(note_id)
        note_data = redis_client.get(note_key)
        
        if not note_data:
            # 如果 Redis 中沒有，從 MongoDB 獲取
            note = await notes_collection.find_one({"id": note_id}, {"_id": 0})
            if not note:
                logger.warning(f"更新標題失敗，筆記不存在: {note_id}")
                raise HTTPException(status_code=404, detail="筆記不存在")
            note_data = json.dumps(note, ensure_ascii=False)
        
        try:
            # 更新標題
            note = json.loads(note_data)
            note["title"] = title
            note["updated_at"] = get_utc_now()
            
            # 更新 Redis
            redis_client.set(note_key, json.dumps(note, ensure_ascii=False))
            
            # 更新 MongoDB
            await notes_collection.update_one(
                {"id": note_id},
                {"$set": {"title": title, "updated_at": note["updated_at"]}}
            )
            
            logger.info(f"更新筆記標題成功: {note_id}")
            return note
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新筆記標題失敗: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="更新標題失敗")
    
    @staticmethod
    async def update_note_content(note_id: str, title: str, content: str, created_at: str) -> dict:
        """
        更新筆記內容（透過 Socket.IO）
        
        Args:
            note_id: 筆記 ID
            title: 標題
            content: 內容
            created_at: 創建時間
            
        Returns:
            更新後的筆記資料
        """
        note_key = get_redis_key(note_id)
        new_data = {
            "id": note_id,
            "title": title,
            "content": content,
            "created_at": created_at,
            "updated_at": get_utc_now()
        }
        
        try:
            # 更新 Redis
            redis_client.set(note_key, json.dumps(new_data, ensure_ascii=False))
            
            # 同時寫入 MongoDB（確保資料持久化）
            await notes_collection.update_one(
                {"id": note_id},
                {"$set": new_data},
                upsert=True
            )
            
            logger.debug(f"更新筆記內容成功: {note_id}")
            return new_data
        except Exception as e:
            logger.error(f"更新筆記內容失敗: {e}", exc_info=True)
            raise


# 創建服務實例
note_service = NoteService()
