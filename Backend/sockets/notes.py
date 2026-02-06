"""
Socket.IO 事件處理
"""
import socketio
from services.note_service import note_service
from utils.logger import setup_logger

logger = setup_logger(__name__)


def register_socket_handlers(sio: socketio.AsyncServer):
    """註冊所有 Socket.IO 事件處理器"""
    
    @sio.event
    async def connect(sid, environ):
        logger.info(f"Client connected: {sid}")
    
    @sio.event
    async def disconnect(sid):
        logger.info(f"Client disconnected: {sid}")
    
    @sio.event
    async def join(sid, data):
        room = data.get('note_id')
        if room:
            await sio.enter_room(sid, room)
            logger.info(f"Client {sid} joined note {room}")
        else:
            logger.warning(f"Client {sid} join event missing note_id")
    
    @sio.event
    async def leave(sid, data):
        room = data.get('note_id')
        if room:
            await sio.leave_room(sid, room)
            logger.info(f"Client {sid} left note {room}")
        else:
            logger.warning(f"Client {sid} leave event missing note_id")
    
    @sio.on("update_note")
    async def update_note(sid, data):
        """處理筆記更新事件"""
        try:
            note_id = data.get('note_id')
            if not note_id:
                logger.warning(f"update_note event missing note_id from {sid}")
                return
            
            title = data.get("title", "Untitled Note")
            content = data.get("content", "")
            created_at = data.get("created_at", "")
            
            # 更新筆記內容
            new_data = await note_service.update_note_content(
                note_id=note_id,
                title=title,
                content=content,
                created_at=created_at
            )
            
            # 廣播更新給房間內的所有用戶
            await sio.emit('note_update', new_data, room=note_id)
            logger.debug(f"筆記更新已廣播: {note_id}")
            
        except Exception as e:
            logger.error(f"處理 update_note 事件失敗: {e}", exc_info=True)
