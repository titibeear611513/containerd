from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from model.note import NoteCreate, Note
from motor.motor_asyncio import AsyncIOMotorClient
import socketio
import redis
import json
import uuid
from datetime import datetime, timezone
from typing import List

# 初始化 Socket.IO
app = FastAPI()
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sio_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app, socketio_path="/ws/socket.io")

print("ws mt")
# Redis 連接
try:
    redis_client = redis.Redis(
        host='redis',  # Docker 服務名稱
        # host='localhost',  # for local build
        port=6379,
        decode_responses=True
    )
except Exception as e:
    print(f"Redis 連接失敗: {e}")
    raise

# MongoDB 連接
mongo_client = AsyncIOMotorClient("mongodb://mongodb:27017")  # Docker 服務名稱
# mongo_client = AsyncIOMotorClient("mongodb://admin:user@1.1.1.1:27017")  # for local build
db = mongo_client["note_db"]
notes_collection = db["notes"]


def safe_parse_iso_datetime(s):
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

# Socket.IO 事件處理
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def join(sid, data):
    room = data['note_id']
    await sio.enter_room(sid, room)
    print(f"Client {sid} joined note {room}")

@sio.event
async def leave(sid, data):
    room = data['note_id']
    await sio.leave_room(sid, room)
    print(f"Client {sid} left note {room}")

@sio.on("update_note")
async def update(sid, data):
    note_id = data['note_id']
    title = data.get("title", "Untitled Note")
    content = data['content']
    create_at = data['created_at']
    now = datetime.utcnow().isoformat()

    # 更新 Redis
    note_key = f"note:{note_id}"
    new_data = {
        "id": note_id,
        "title": title,
        "content": content,
        "created_at": create_at,
        "updated_at": now
    }
    # Redis 覆蓋（Last Write Wins）
    redis_client.set(note_key, json.dumps(new_data))
    
    # 廣播更新
    await sio.emit('note_update', new_data, room=note_id)

#提供前端使用者傳入title創建筆記，並回傳筆記 ID  
@app.post("/api/notes")
async def create_note(note: NoteCreate):
    note_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    note_data = {
        "id": note_id,
        "title": note.title,
        "content": "",
        "created_at": now,
        "updated_at": now
    }
    note_key = f"note:{note_id}"
    # 1. 快取到 Redis
    redis_client.set(note_key, json.dumps(note_data))
    # 2. 寫入 MongoDB
    await notes_collection.insert_one(note_data)
    # 3. 從 MongoDB 讀取，確保返回正確的格式 (用投影（projection）排除 _id)
    created_note = await notes_collection.find_one({"id": note_id}, {"_id": 0})
    return created_note


#提供前端使用者取得所有筆記以顯示在列表中
@app.get("/api/notes", response_model=List[Note])
async def list_notes():
    notes = []
    keys = []
    # 從 Redis 獲取所有筆記，Redis.py不能使用await
    for key in redis_client.scan_iter(match="note:*"):
        keys.append(key)

    if keys:
        for key in keys:
            raw = redis_client.get(key)
            if raw:
                note = json.loads(raw)
                notes.append(note)
    else:
        # 從 MongoDB fallback 
        cursor = notes_collection.find({}, {"_id": 0})  # 排除 _id
        async for note in cursor:
            notes.append(note)
            redis_client.set(f"note:{note['id']}", json.dumps(note))

    notes.sort(key=lambda n: safe_parse_iso_datetime(n["created_at"]), reverse=True)
    return notes

#提供前端使用者取得指定筆記
@app.get("/api/notes/{note_id}")
async def get_note(note_id: str):
    note_key = f"note:{note_id}"
    data = redis_client.get(note_key)

    if data:
        return json.loads(data)

    # 若 Redis 沒有 → 查 MongoDB
    note_data = await notes_collection.find_one({"id": note_id}, {"_id": 0})  # 排除 _id
    if note_data:
        # 同步到 Redis 快取，Redis.py不能使用await
        redis_client.set(note_key, json.dumps(note_data))
        return note_data

    raise HTTPException(status_code=404, detail="筆記不存在")


@app.delete("/api/notes/{note_id}")
async def delete_note(note_id: str):
    note_key = f"note:{note_id}"
    # 1. 刪除 Redis 快取
    redis_client.delete(note_key)

    # 2. 刪除 MongoDB 文件
    result = await notes_collection.delete_one({"id": note_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="筆記不存在")

    return {"message": "筆記已刪除"}

@app.put("/api/notes/{note_id}/title")
async def update_note_title(note_id: str, title_update: dict):
    try:
        # 從 Redis 獲取筆記
        note_key = f"note:{note_id}"
        note_data = redis_client.get(note_key)
        
        if not note_data:
        # if True:
            # 如果 Redis 中沒有，從 MongoDB 獲取
            note = await notes_collection.find_one({"id": note_id}, {"_id": 0})
            if not note:
                raise HTTPException(status_code=404, detail="筆記不存在")
            note_data = json.dumps(note)
        
        # 更新標題
        note = json.loads(note_data)
        note["title"] = title_update["title"]
        note["updated_at"] = datetime.now().isoformat()
        
        # 更新 Redis
        redis_client.set(note_key, json.dumps(note))
        
        # 更新 MongoDB
        await notes_collection.update_one(
            {"id": note_id},
            {"$set": {"title": title_update["title"], "updated_at": note["updated_at"]}}
        )
        
        # 發送 Socket.IO 事件
        await sio.emit("note_update", {
            "id": note_id,
            "title": title_update["title"],
            "content": note["content"]
        })
        
        return note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
