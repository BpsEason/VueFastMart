# VueFastMart

VueFastMart 是一個基於 Vue.js 和 FastAPI 的現代電商平台，提供產品瀏覽、購物車管理和用戶認證功能。專案設計注重新手友好，支援前端懶加載、API 快取和安全認證，適合學習全端開發。

## 功能

### 前端功能
- **產品列表與詳情**：展示產品資訊（名稱、描述、價格、庫存），支援圖片懶加載。
- **購物車管理**：添加、移除購物車項目，與後端 API 同步，使用 Pinia 狀態管理。
- **用戶認證**：支援註冊和登入，使用 JWT 認證。
- **響應式設計**：使用 Tailwind CSS，適配手機和桌面。

### 後端 API
- **認證**：`POST /auth/register`, `POST /auth/token` - 用戶註冊和登入。
- **產品**：`GET /products/` - 分頁查詢產品，`GET /products/{id}` - 產品詳情。
- **購物車**：`GET /cart/` - 獲取購物車，`POST /cart/` - 添加項目，`DELETE /cart/{id}` - 移除項目。
- **健康檢查**：`GET /health` - 檢查 API 和資料庫狀態。

## 技術棧
- **前端**：Vue.js 3, Pinia, Vue Router, Axios, Tailwind CSS, Vite
- **後端**：FastAPI, SQLAlchemy, SQLite/PostgreSQL, Redis（快取）
- **測試**：Vitest（前端），Pytest（後端）

## 專案結構
```
VueFastMart/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── products.py
│   │   │   └── cart.py
│   │   ├── database.py
│   │   ├── cache.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_products.py
│   │   └── test_cart.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ProductCard.vue
│   │   ├── store/
│   │   │   ├── auth.js
│   │   │   └── cart.js
│   │   ├── views/
│   │   │   ├── ProductList.vue
│   │   │   ├── ProductDetail.vue
│   │   │   ├── Cart.vue
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   └── router/
│   │       └── index.js
│   ├── tests/
│   │   ├── ProductList.test.js
│   │   └── Cart.test.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── package.json
│   └── .env.example
├── create_project.py
└── README.md
```

## 設置與運行

### 前提條件
- **Node.js**: v18 或更高版本
- **Python**: 3.10 或更高版本
- **Redis**: 用於快取（可選）
- **Git**: 用於版本控制

### 設置後端
1. 克隆專案：
   ```bash
   git clone https://github.com/BpsEason/VueFastMart.git
   cd VueFastMart/backend
   ```
2. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置環境變數：
   ```bash
   cp .env.example .env
   ```
   編輯 `.env`，設置：
   ```env
   DATABASE_URL=sqlite:///./vuefastmart.db
   SECRET_KEY=your-secret-key
   REDIS_HOST=localhost
   REDIS_PORT=6379
   FRONTEND_URL=http://localhost:5173
   ```
   生成 `SECRET_KEY`：
   ```bash
   openssl rand -hex 32
   ```
4. 啟動後端：
   ```bash
   uvicorn app.main:app --reload
   ```
   訪問 `http://localhost:8000/docs` 查看 API 文件，`http://localhost:8000/health` 檢查健康狀態。

### 設置前端
1. 進入前端目錄：
   ```bash
   cd frontend
   ```
2. 安裝依賴：
   ```bash
   npm install
   ```
3. 配置環境變數：
   ```bash
   cp .env.example .env
   ```
   編輯 `.env`，設置：
   ```env
   VITE_API_URL=http://localhost:8000
   ```
4. 啟動前端：
   ```bash
   npm run dev
   ```
   訪問 `http://localhost:5173`。

### 運行測試
- **後端測試**：
   ```bash
   cd backend
   pytest tests/ --cov=app --cov-report=html
   ```
- **前端測試**：
   ```bash
   cd frontend
   npm run test
   ```

## 部署指引

### 部署前端到 Vercel
1. 將前端程式碼推送到 GitHub。
2. 在 Vercel 創建新專案，連接到 GitHub 倉庫。
3. 設置環境變數：
   - `VITE_API_URL`: 後端 API 地址（例如 `https://vuefastmart-api.onrender.com`）
4. 部署並獲取前端 URL，更新後端 `.env` 的 `FRONTEND_URL`。

### 部署後端到 Render
1. 將後端程式碼推送到 GitHub。
2. 在 Render 創建新 Web Service，選擇 Python 環境。
3. 設置環境變數：
   - `DATABASE_URL`: PostgreSQL URL（由 Render 提供）
   - `SECRET_KEY`: 安全密鑰
   - `FRONTEND_URL`: 前端部署地址
   - `REDIS_HOST` 和 `REDIS_PORT`（若使用 Redis）
4. 部署並驗證 `/health` 端點。

## 開發與貢獻
1. 提交問題或功能請求到 GitHub Issues。
2. Fork 專案，創建分支，提交 Pull Request。
3. 遵循 PEP 8（Python）和 ESLint（JavaScript）規範。

## 故障排除
- **CORS 錯誤**：檢查後端 `.env` 的 `FRONTEND_URL` 是否與前端地址一致。
- **API 請求失敗**：確認 `vite.config.js` 的代理設置和後端是否運行。
- **資料庫錯誤**：檢查 `DATABASE_URL` 和資料庫服務。
- 查看日誌：
  - 後端：`uvicorn` 輸出或 `tail -f uvicorn.log`
  - 前端：瀏覽器開發者工具（F12）Network 標籤

## 致謝
感謝 FastAPI、Vue.js 和 Tailwind CSS 社群的優秀工具！本專案受《Python 電商教學》啟發，旨在幫助新手學習全端開發。