# VueFastMart

VueFastMart 是一個現代化的電子商務平台，使用 Vue.js 構建前端，FastAPI 構建後端，提供產品瀏覽、購物車管理和用戶認證功能。專案支援管理員產品管理、Redis 快取、JWT 認證，並提供完整的測試覆蓋和 Docker 部署選項。

## 功能

- **用戶認證**：
  - 註冊：用戶可以創建帳戶（電子郵件和密碼，密碼需至少 8 個字符，包含字母和數字）。
  - 登入：使用電子郵件和密碼生成 JWT 訪問令牌。
  - 用戶資訊：查看當前用戶資料（`/api/auth/users/me`）。
- **產品管理**：
  - 瀏覽產品：分頁顯示產品列表，包含名稱、描述、價格、庫存和圖片。
  - 搜索產品：按名稱模糊搜索產品。
  - 管理員操作：管理員可創建、更新、刪除產品。
- **購物車**：
  - 添加項目：將產品加入購物車，自動檢查庫存並更新。
  - 查看購物車：顯示用戶的購物車項目，包含產品詳情和總價。
  - 更新數量：修改購物車項目數量，確保庫存充足。
  - 移除項目：從購物車中刪除項目並恢復庫存。
- **性能與安全**：
  - Redis 快取：產品列表查詢快取 60 秒，提升性能。
  - JWT 認證：保護購物車和管理員端點。
  - CORS 和安全標頭：防止跨站請求和安全漏洞。
- **測試與部署**：
  - 自動化測試：後端使用 Pytest，前端使用 Jest。
  - Docker 支援：使用 Docker Compose 快速部署。

## 技術棧

- **前端**：
  - Vue.js 3：響應式前端框架。
  - Vue Router：客戶端路由。
  - Axios：處理 API 請求。
  - Jest：前端單元測試。
- **後端**：
  - FastAPI：高性能 API 框架。
  - SQLAlchemy：ORM 資料庫操作。
  - Redis：快取產品數據。
  - Pydantic：數據驗證和序列化。
  - Python-Jose & Passlib：JWT 和密碼哈希。
  - Pytest：後端單元測試。
- **資料庫**：
  - SQLite（開發環境）。
  - PostgreSQL（生產環境，需配置）。
- **部署**：
  - Docker & Docker Compose：容器化部署。
  - Gunicorn & Nginx（生產建議）。

## 專案結構

```plaintext
VueFastMart/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── products.py
│   │   │   └── cart.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   └── cart.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   └── cart.py
│   │   ├── database.py
│   │   ├── cache.py
│   │   ├── main.py
│   │   └── tests/
│   │       ├── test_auth.py
│   │       ├── test_products.py
│   │       └── test_cart.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductCard.vue
│   │   │   ├── ProductList.vue
│   │   │   ├── ProductDetail.vue
│   │   │   ├── Cart.vue
│   │   │   ├── Register.vue
│   │   │   └── Login.vue
│   │   ├── utils/
│   │   │   └── cart.js
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── router.js
│   ├── tests/
│   │   ├── ProductList.test.js
│   │   └── Cart.test.js
│   ├── package.json
│   ├── vite.config.js
│   └── .env.example
└── README.md
```

## 先決條件

- **Node.js**：>= 18
- **Python**：>= 3.12
- **Redis**：用於快取（可選，若禁用快取則不需要）
- **Docker**：若使用容器化部署
- **PostgreSQL**：生產環境（可選，開發使用 SQLite）

## 安裝

### 1. 生成專案

運行 `create_project.py` 生成專案結構：

```bash
python create_project.py
cd VueFastMart
```

### 2. 設置後端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

編輯 `.env`，設置 `SECRET_KEY` 和其他變數：

```bash
# 生成隨機 SECRET_KEY
openssl rand -hex 32
```

範例 `.env`：

```plaintext
DATABASE_URL=sqlite:///./vuefastmart.db
SECRET_KEY=your-generated-secret-key
FRONTEND_URL=http://localhost:5173
REDIS_HOST=localhost
REDIS_PORT=6379
```

啟動後端：

```bash
uvicorn app.main:app --reload
```

訪問 `http://localhost:8000/docs` 查看 API 文檔，`http://localhost:8000/health` 檢查健康狀態。

### 3. 設置前端

```bash
cd frontend
npm install
cp .env.example .env
```

編輯 `.env`：

```plaintext
VITE_API_URL=http://localhost:8000
```

啟動前端：

```bash
npm run dev
```

訪問 `http://localhost:5173` 查看應用。

### 4. 使用 Docker

```bash
docker-compose up -d
```

- 後端運行於 `http://localhost:8000`。
- Redis 運行於 `localhost:6379`。
- 前端需單獨運行（`npm run dev`），或自行添加前端 Dockerfile。

## API 文檔

FastAPI 提供內建 Swagger UI，訪問以下地址查看和測試 API：

- **Swagger UI**：`http://localhost:8000/docs`
- **ReDoc**：`http://localhost:8000/redoc`

主要端點：

- **認證**：
  - `POST /api/auth/register`：註冊用戶
  - `POST /api/auth/token`：登入獲取 JWT
  - `GET /api/auth/users/me`：獲取當前用戶資訊
- **產品**：
  - `GET /api/products/`：分頁獲取產品列表
  - `GET /api/products/search?name=xxx`：搜索產品
  - `GET /api/products/{id}`：獲取單一產品
  - `POST /api/products/`：創建產品（管理員）
  - `PUT /api/products/{id}`：更新產品（管理員）
  - `DELETE /api/products/{id}`：刪除產品（管理員）
- **購物車**：
  - `POST /api/cart/`：添加產品到購物車
  - `GET /api/cart/`：獲取購物車項目
  - `PUT /api/cart/{id}`：更新購物車項目數量
  - `DELETE /api/cart/{id}`：移除購物車項目

## 測試

### 後端測試

```bash
cd backend
pytest tests/ --cov=app --cov-report=html
```

生成覆蓋率報告於 `backend/htmlcov/`。

### 前端測試

```bash
cd frontend
npm run test
```

## 部署

### 生產環境建議

1. **資料庫**：
   - 替換 SQLite 為 PostgreSQL：
     ```plaintext
     DATABASE_URL=postgresql://user:password@host:5432/vuefastmart
     ```
   - 確保安裝 `psycopg2-binary`（已包含在 `requirements.txt`）。

2. **後端**：
   - 使用 Gunicorn 運行 FastAPI：
     ```bash
     gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
     ```
   - 配置 Nginx 作為反向代理：
     ```nginx
     server {
         listen 80;
         server_name your-domain.com;
         location / {
             proxy_pass http://localhost:8000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
         }
     }
     ```

3. **前端**：
   - 構建靜態文件：
     ```bash
     cd frontend
     npm run build
     ```
   - 將 `dist/` 目錄部署到 Nginx 或 CDN。

4. **環境變數**：
   - 確保 `.env` 包含正確的 `SECRET_KEY`、`DATABASE_URL` 和 `FRONTEND_URL`。

5. **Docker**：
   - 更新 `docker-compose.yml` 添加前端服務：
     ```yaml
     frontend:
       build:
         context: ./frontend
       ports:
         - "5173:5173"
       volumes:
         - ./frontend:/app
     ```

## 問題排查

- **後端無法啟動**：
  - 檢查 `.env` 中的 `SECRET_KEY` 和 `DATABASE_URL`。
  - 確保 Redis 運行（`redis-server`）。
- **前端 API 請求失敗**：
  - 檢查 `VITE_API_URL` 是否正確。
  - 確保後端運行且 CORS 配置正確。
- **測試失敗**：
  - 確保密碼符合要求（`Secure123`）。
  - 檢查 SQLite/PostgreSQL 連線。

## 未來改進

- 添加訂單管理功能。
- 實現產品分類和篩選。
- 添加圖片上傳功能（例如 S3 整合）。
- 增強安全措施（如密碼重置、兩步驗證）。

## 貢獻

歡迎提交問題或拉取請求到 [GitHub 倉庫](https://github.com/BpsEason/VueFastMart)。請遵循以下步驟：

1. Fork 倉庫
2. 創建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'Add xxx'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 創建拉取請求

## 許可證

本專案採用 MIT 許可證。