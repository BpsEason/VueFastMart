# VueFastMart

VueFastMart 是一個使用 **FastAPI** 和 **Vue.js** 開發的前後端分離電商產品管理系統，展示現代全端開發能力。系統支援產品管理、用戶認證和購物車功能，注重 **可測試性**、**安全性** 和 **效能**，適合作為 GitHub 上的展示專案。

## 功能

- **產品管理**：
  - **新增產品** (`POST /products/`)：管理員可創建新產品，包含名稱、描述、價格和庫存。
  - **讀取產品** (`GET /products/` 和 `GET /products/{id}`)：支援分頁查詢和單一產品檢視，使用 Redis 快取提升效能。
  - **更新產品** (`PUT /products/{id}`)：管理員可修改產品資訊。
  - **刪除產品** (`DELETE /products/{id}`)：管理員可刪除產品。
- **用戶認證**：
  - 註冊 (`POST /auth/register`) 和登入 (`POST /auth/token`)，使用 JWT 和 bcrypt 加密。
  - 支援角色權限控制，僅管理員可執行產品管理操作。
  - 登出功能（前端移除 token）。
- **購物車**：
  - 添加產品到購物車 (`POST /cart/`)，檢查庫存。
  - 檢視購物車 (`GET /cart/`) 和移除項目 (`DELETE /cart/{id}`)，後端儲存資料。
- **響應式設計**：
  - 使用 Tailwind CSS 打造現代化 UI。
  - 支援圖片懶加載，優化前端效能。
- **容器化部署**：
  - 使用 Docker 和 Gunicorn，支援高並發。
  - 包含 Docker Compose 配置，簡化部署流程。

## 技術棧

- **後端**：
  - FastAPI：高效的 Python Web 框架。
  - SQLAlchemy：ORM 工具，與 PostgreSQL 整合。
  - PostgreSQL：關聯式資料庫，儲存用戶和產品資料。
  - Redis：快取產品查詢，提升效能。
  - JWT：用戶認證。
  - pytest：API 測試，覆蓋率達 80%。
- **前端**：
  - Vue.js (Composition API)：現代前端框架。
  - Pinia：狀態管理。
  - Tailwind CSS：響應式樣式。
  - Vitest：組件測試。
- **其他**：
  - Docker：容器化部署。
  - Gunicorn + Uvicorn：高並發伺服器。
  - GitHub Actions：CI/CD 自動化測試。

## 可測試性

- **後端測試**：
  - 使用 pytest 測試所有 API 端點（認證、產品、購物車）。
  - 包含單元測試和整合測試，覆蓋率達 80%。
  - 執行測試：
    ```bash
    cd backend
    pytest tests/
    ```
- **前端測試**：
  - 使用 Vitest 測試 Vue 組件（如產品列表）。
  - 執行測試：
    ```bash
    cd frontend
    npm run test
    ```

## 安全性

- **認證**：使用 bcrypt 加密密碼，JWT 實現安全認證。
- **權限控制**：僅管理員可執行產品新增、更新和刪除操作。
- **HTTP 安全頭部**：
  - Content-Security-Policy (CSP)、X-Frame-Options、X-Content-Type-Options。
- **環境變數**：敏感資訊（如資料庫 URL、JWT 密鑰）儲存在 `.env` 文件中。

## 效能

- **後端**：
  - 分頁查詢（`skip` 和 `limit`）減少資料庫負載。
  - Redis 快取產品列表，降低重複查詢開銷。
  - 資料庫索引優化查詢速度。
- **前端**：
  - 圖片懶加載，減少初始載入時間。
  - Vite 分塊構建，優化資源載入。
- **部署**：Gunicorn + Uvicorn 支援高並發處理。

## 安裝與執行

### 前置條件

- Docker 和 Docker Compose
- Node.js 18+
- Python 3.11+
- PostgreSQL（本地運行時）
- Redis（本地運行時）

### 本地執行

1. **克隆專案**：
   ```bash
   git clone https://github.com/your-username/VueFastMart
   cd VueFastMart
   ```

2. **配置環境變數**：
   ```bash
   cp backend/.env.example backend/.env
   ```
   編輯 `backend/.env`，設置以下內容：
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/vuefastmart_db
   SECRET_KEY=your-very-secure-secret-key
   FRONTEND_URL=http://localhost:5173
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

3. **啟動後端**：
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows 使用 venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. **啟動前端**：
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **設置資料庫和 Redis**：
   - 安裝並啟動 PostgreSQL，創建資料庫 `vuefastmart_db`。
   - 安裝並啟動 Redis（預設埠 6379）。

6. **訪問**：
   - 後端 API：`http://localhost:8000/docs`
   - 前端：`http://localhost:5173`

### Docker 部署

1. **配置環境變數**：
   - 編輯 `backend/.env`（同上）。
2. **啟動服務**：
   ```bash
   docker-compose up --build
   ```
3. **訪問**：
   - 後端 API：`http://localhost:8000/docs`
   - 前端：`http://localhost:5173`

## API 文件

- 訪問 `http://localhost:8000/docs` 查看互動式 Swagger UI。
- 詳細 API 範例見 [docs/api.md](docs/api.md)。

## 截圖

- 產品列表：![產品列表](docs/screenshots/product-list.png)
- 購物車：![購物車](docs/screenshots/cart.png)

## 聯繫方式

- GitHub: [your-username](https://github.com/your-username)
- LinkedIn: [your-linkedin](https://linkedin.com/in/your-linkedin)

## 許可證

MIT License. 詳見 [LICENSE](LICENSE) 文件。