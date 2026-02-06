from pydantic import BaseModel, Field
from typing import Optional

class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="筆記標題")

class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="筆記標題")
    content: Optional[str] = Field(None, description="筆記內容")

class NoteTitleUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="筆記標題")

class Note(BaseModel):
    id: str
    title: str
    content: str
    created_at: str
    updated_at: str