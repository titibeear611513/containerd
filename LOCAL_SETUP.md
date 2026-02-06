# 本地啟動指南（不使用 Docker）

本指南說明如何在不使用 Docker 的情況下啟動此專案。

## 前置需求

### 1. 安裝必要服務

#### MongoDB
```bash
# macOS (使用 Homebrew)
brew install mongodb-community
brew services start mongodb-community

# 或使用官方安裝包
# https://www.mongodb.com/try/download/community

# 確認 MongoDB 運行在 27017 端口
mongosh
```

#### Redis
```bash
# macOS (使用 Homebrew)
brew install redis
brew services start redis

# 或使用官方安裝包
# https://redis.io/download

# 確認 Redis 運行在 6379 端口
redis-cli ping
# 應該回傳 PONG
```

### 2. 安裝 Python 依賴

**方法 1：使用 pip3（推薦）**
```bash
cd Backend
pip3 install -r requirements.txt
```

**方法 2：使用 python3 -m pip**
```bash
cd Backend
python3 -m pip install -r requirements.txt
```

**方法 3：使用虛擬環境（最佳實踐）**
```bash
cd Backend
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 安裝 Node.js 依賴

```bash
cd Frontend
npm install
```

## 啟動步驟

### 步驟 1: 啟動 MongoDB

確保 MongoDB 服務正在運行：

```bash
# macOS
brew services start mongodb-community

# 或直接啟動
mongod --config /usr/local/etc/mongod.conf
```

### 步驟 2: 啟動 Redis

確保 Redis 服務正在運行：

```bash
# macOS
brew services start redis

# 或直接啟動
redis-server
```

### 步驟 3: 啟動後端服務

**如果使用虛擬環境：**
```bash
cd Backend
source venv/bin/activate  # macOS/Linux
# 或 Windows: venv\Scripts\activate
uvicorn main:sio_app --host 0.0.0.0 --port 8080 --reload
```

**如果沒有使用虛擬環境：**
```bash
cd Backend
python3 -m uvicorn main:sio_app --host 0.0.0.0 --port 8080 --reload
```

後端應該會在 `http://localhost:8080` 啟動。

### 步驟 4: 啟動前端服務

開啟新的終端視窗：

```bash
cd Frontend
npm run dev
```

前端應該會在 `http://localhost:3000` 啟動。

## 訪問應用

打開瀏覽器訪問：`http://localhost:3000`

## 配置說明

### 後端配置

後端預設使用以下配置：
- **Redis**: `localhost:6379`
- **MongoDB**: `mongodb://localhost:27017`

如果需要修改，請編輯 `Backend/main.py` 中的連接設定。

### 前端配置

前端預設使用以下配置：
- **API URL**: `http://localhost:8080/api`
- **Socket URL**: `http://localhost:8080`

如果需要修改，請編輯：
- `Frontend/src/services/api.ts`
- `Frontend/src/services/socket.ts`

## 常見問題

### pip 命令找不到

在 macOS 上，系統通常只有 `pip3` 而沒有 `pip`。

**解決方案：**

1. **使用 pip3：**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **使用 python3 -m pip：**
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. **使用虛擬環境（推薦）：**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt  # 在虛擬環境中可以使用 pip
   ```

### MongoDB 連接失敗

1. 確認 MongoDB 服務正在運行：
   ```bash
   brew services list | grep mongodb
   ```

2. 檢查 MongoDB 是否監聽正確端口：
   ```bash
   lsof -i :27017
   ```

### Redis 連接失敗

1. 確認 Redis 服務正在運行：
   ```bash
   redis-cli ping
   ```

2. 檢查 Redis 是否監聽正確端口：
   ```bash
   lsof -i :6379
   ```

### 端口已被佔用

如果 8080 或 3000 端口已被佔用：

**後端**：修改啟動命令中的端口
```bash
uvicorn main:sio_app --host 0.0.0.0 --port 8081 --reload
```
然後記得修改前端的 API URL。

**前端**：修改 `package.json` 中的 dev 腳本，或使用：
```bash
npm run dev -- -p 3001
```

## 停止服務

1. **停止前端**：在運行前端的終端按 `Ctrl + C`
2. **停止後端**：在運行後端的終端按 `Ctrl + C`
3. **停止 Redis**：
   ```bash
   brew services stop redis
   # 或
   redis-cli shutdown
   ```
4. **停止 MongoDB**：
   ```bash
   brew services stop mongodb-community
   # 或
   mongosh --eval "db.adminCommand('shutdown')"
   ```
