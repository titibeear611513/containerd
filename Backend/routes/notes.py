"""
筆記相關的 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import List

from model.note import Note, NoteCreate, NoteTitleUpdate
from services.note_service import note_service
from utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api/notes", tags=["notes"])


@router.post("", response_model=Note)
async def create_note(note: NoteCreate):
    """創建新筆記"""
    return await note_service.create_note(note)


@router.get("", response_model=List[Note])
async def list_notes():
    """獲取所有筆記列表"""
    return await note_service.list_notes()


@router.get("/{note_id}", response_model=Note)
async def get_note(note_id: str):
    """獲取指定筆記"""
    return await note_service.get_note(note_id)


@router.delete("/{note_id}")
async def delete_note(note_id: str):
    """刪除指定筆記"""
    return await note_service.delete_note(note_id)


@router.put("/{note_id}/title", response_model=Note)
async def update_note_title(note_id: str, title_update: NoteTitleUpdate):
    """更新筆記標題"""
    return await note_service.update_note_title(note_id, title_update.title)
