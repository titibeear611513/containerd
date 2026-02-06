"""
FastAPI 應用程式入口
負責組裝所有模組：路由、Socket.IO、資料庫連接等
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from config import settings, socketio_cors_origins
from utils.logger import setup_logger
from routes.notes import router as notes_router
from sockets.notes import register_socket_handlers

# 初始化日誌系統
logger = setup_logger(__name__)

# 初始化 FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="多人協作筆記系統 API",
    version="1.0.0"
)

# 初始化 Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=socketio_cors_origins,
    logger=True,
    engineio_logger=True
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# 組裝 Socket.IO 和 FastAPI
sio_app = socketio.ASGIApp(
    socketio_server=sio,
    other_asgi_app=app,
    socketio_path=settings.SOCKETIO_PATH
)

# 註冊路由
app.include_router(notes_router)

# 註冊 Socket.IO 事件處理器
register_socket_handlers(sio)

# 初始化資料庫連接（會在導入時自動連接）
from db.redis_client import redis_client  # noqa: E402
from db.mongo_client import notes_collection  # noqa: E402

logger.info("應用程式初始化完成")
