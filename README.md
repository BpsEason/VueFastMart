# VueFastMart

**VueFastMart** 是一個簡單易學的電商產品管理系統，專為探索 Web 開發的初學者設計。這個開源專案使用 **Python FastAPI** 打造後端 API，**Vue.js** 實現互動式前端，搭配 **SQLite** 儲存資料，並以 **pytest** 和 **Vitest** 確保程式碼品質。無論你是 Python 新手還是想試試全端開發，VueFastMart 都是你的理想起點！

## 功能

- **產品管理**：展示產品列表，包含名稱、描述、價格和庫存。
- **用戶認證**：支援用戶註冊，未來將加入登入功能。
- **響應式前端**：使用 Vue.js 和 Tailwind CSS，提供現代化、行動友好的介面。
- **高品質測試**：後端使用 pytest，前端使用 Vitest，覆蓋率達 85% 以上。
- **未來計劃**：
  - 購物車功能：支援添加和移除商品。
  - 用戶登入與權限：使用 JWT 實現安全認證。
  - 產品搜尋與分頁：提升用戶體驗。

## 技術棧

- **後端**：FastAPI, SQLAlchemy, SQLite, python-jose, passlib
- **前端**：Vue.js 3, Vue Router, Axios, Tailwind CSS, Pinia（未來購物車用）
- **測試**：pytest (後端), Vitest (前端)
- **其他**：Vite (前端構建), GitHub Actions (未來 CI/CD)

## 快速開始

### 環境要求

- Python 3.11+
- Node.js 18+
- Git

### 安裝步驟

1. **複製專案**：
   ```bash
   git clone https://github.com/BpsEason/VueFastMart.git
   cd VueFastMart
   ```

2. **設置後端**：
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **設置前端**：
   ```bash
   cd ../frontend
   npm install
   ```

4. **運行後端**：
   ```bash
   cd ../backend
   uvicorn app.main:app --reload
   ```
   訪問 `http://localhost:8000/docs` 查看 API 文件。

5. **運行前端**：
   ```bash
   cd ../frontend
   npm run dev
   ```
   訪問 `http://localhost:5173` 查看產品列表頁面。

### 資料庫初始化

- 首次運行後端時，SQLite 資料庫（`vuefastmart.db`）會自動創建。
- 可手動添加產品資料到 `products` 表，未來將提供初始化腳本。

## 測試

### 後端測試

使用 pytest 測試 API 端點：
```bash
cd backend
pytest tests/
```

### 前端測試

使用 Vitest 測試 Vue 組件：
```bash
cd frontend
npm run test
```

目前測試覆蓋：
- 產品列表渲染（`ProductList.test.js`）
- 購物車功能（`Cart.test.js`，待完整實現）

## 專案結構

```
VueFastMart/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI 應用入口
│   │   ├── database.py       # 資料庫配置
│   │   ├── models/          # SQLAlchemy 模型
│   │   ├── schemas/         # Pydantic 資料結構
│   │   ├── api/            # API 路由
│   ├── tests/              # pytest 測試
├── frontend/
│   ├── src/
│   │   ├── views/          # Vue 組件 (ProductList.vue, Cart.vue)
│   │   ├── stores/         # Pinia 狀態管理
│   │   ├── assets/         # Tailwind CSS
│   ├── tests/              # Vitest 測試
├── docs/                   # 文件 (教學文章)
├── README.md
```

## 貢獻

歡迎為 VueFastMart 貢獻程式碼、文件或建議！請遵循以下步驟：

1. Fork 本專案：https://github.com/BpsEason/VueFastMart
2. 創建特性分支：
   ```bash
   git checkout -b feature/你的功能
   ```
3. 提交變更：
   ```bash
   git commit -m "新增你的功能"
   ```
4. 推送到遠端：
   ```bash
   git push origin feature/你的功能
   ```
5. 提交 Pull Request，描述你的變更。

請閱讀 [CONTRIBUTING.md](CONTRIBUTING.md)（未來添加）以了解詳細規範。

### 待辦事項

- [ ] 實現購物車 API 和前端頁面
- [ ] 添加用戶登入功能
- [ ] 設置 GitHub Actions 進行自動測試
- [ ] 撰寫更多單元測試，目標覆蓋率 90%

## 問題與支援

- **問題回報**：請在 GitHub Issues 提交 bug 或建議：https://github.com/BpsEason/VueFastMart/issues
- **聯繫作者**：Eason (BpsEason) - 透過 GitHub

## 許可證

本專案採用 [MIT License](LICENSE)。詳見許可證文件。

## 感謝

感謝以下開源項目：
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Tailwind CSS](https://tailwindcss.com/)

加入 VueFastMart 的開發，打造屬於你的電商平台！ 🚀