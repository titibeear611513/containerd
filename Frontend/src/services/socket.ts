import { now } from 'lodash';
import socketIO from 'socket.io-client';

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:8080';

class SocketService {
  private socket: ReturnType<typeof socketIO> | null = null;
  private noteUpdateCallback: ((data: any) => void) | null = null;

  connect(userId: string) {
    if (!this.socket) {
      this.socket = socketIO(SOCKET_URL, {
        query: { userId },
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 5,  // 添加重連嘗試次數
        reconnectionDelay: 1000   // 添加重連延遲
      });
      // 添加連接狀態監聽
    this.socket.on('connect', () => {
      console.log('Socket.IO 已連接');
      // 重新註冊事件監聽器
      if (this.noteUpdateCallback) {
        console.log('重新註冊事件監聽器');
        this.socket?.on('note_update', this.noteUpdateCallback);
      }
    });

    this.socket.on('disconnect', () => {
      console.log('Socket.IO 已斷開連接');
    });

    this.socket.on('connect_error', (error: any) => {
      console.error('Socket.IO 連接錯誤:', error);
    });
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  joinNote(noteId: string) {
    if (this.socket) {
      console.log('嘗試加入房間:', noteId);
      this.socket.emit('join', { note_id: noteId });
    }
  }

  leaveNote(noteId: string) {
    if (this.socket) {
      this.socket.emit('leave', { note_id: noteId });
    }
  }

  updateNote(noteId: string, content: string, title: string) {
    if (this.socket) {
      console.log('發送筆記更新:', { noteId, content, title });
      const now = new Date().toISOString();
      this.socket.emit('update_note', {// backend listen to update_note event
        note_id: noteId,
        content,
        title,
        created_at: now  // add created_at
      });
    }
  }

  onNoteUpdate(callback: (data: any) => void) {
    // 先移除舊的監聽器
    if (this.socket && this.noteUpdateCallback) {
      console.log('移除舊的監聽器');
      this.socket.off('note_update', this.noteUpdateCallback);
    }
    this.noteUpdateCallback = callback;
    if (this.socket) {
      console.log('note_update event, backend listen to update_note event');
      this.socket.on('note_update', (data: any) => {
        console.log('收到更新事件:', data);//這裡沒有發生更新事件
        callback(data);
      });
    }
  }

  offNoteUpdate() {
    if (this.socket && this.noteUpdateCallback) {
      this.socket.off('note_update', this.noteUpdateCallback);
      this.noteUpdateCallback = null;
    }
  }
}

export const socketService = new SocketService();
