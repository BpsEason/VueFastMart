# API 文件

以下是 VueFastMart 的 API 端點說明。詳細互動請訪問 `http://localhost:8000/docs` 的 Swagger UI。

## 認證
### 註冊
- **端點**: `POST /auth/register`
- **請求**:
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **回應**:
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "is_admin": false
  }
  ```

### 登入
- **端點**: `POST /auth/token`
- **請求**:
  ```json
  {
    "username": "user@example.com",
    "password": "securepassword"
  }
  ```
- **回應**:
  ```json
  {
    "access_token": "jwt-token",
    "token_type": "bearer"
  }
  ```

## 產品
### 獲取產品列表
- **端點**: `GET /products/?skip=0&limit=10`
- **回應**:
  ```json
  [
    {
      "id": 1,
      "name": "測試產品",
      "description": "這是一個測試產品",
      "price": 100.0,
      "stock": 10