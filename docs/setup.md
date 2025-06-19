# 安裝說明

## 本地開發
1. 安裝依賴：
   - Python 3.11
   - Node.js 18+
   - PostgreSQL
   - Redis
2. 配置環境變數：
   ```bash
   cp backend/.env.example backend/.env
   ```
   編輯 `backend/.env`：
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/vuefastmart_db
   SECRET_KEY=your-very-secure-secret-key
   FRONTEND_URL=http://localhost:5173
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```
3. 啟動後端：
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. 啟動前端：
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Docker 部署
1. 安裝 Docker 和 Docker Compose。
2. 配置環境變數（同上）。
3. 啟動服務：
   ```bash
   docker-compose up --build
   ```
4. 訪問：
   - 後端：`http://localhost:8000/docs`
   - 前端：`http://localhost:5173`