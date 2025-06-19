from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import auth, products, cart
from app.database import engine, Base
from sqlalchemy import inspect
import os

load_dotenv()

# 驗證環境變數
if not os.getenv("FRONTEND_URL"):
    raise ValueError("FRONTEND_URL environment variable is not set")

app = FastAPI(title="VueFastMart API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加安全頭部
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' https://via.placeholder.com; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# 檢查資料庫連線
def check_database_connection():
    try:
        with engine.connect() as connection:
            inspect(engine).get_table_names()
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {str(e)}")

check_database_connection()
Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["認證"])
app.include_router(products.router, prefix="/products", tags=["產品"])
app.include_router(cart.router, prefix="/cart", tags=["購物車"])

@app.get("/")
def read_root():
    return {"message": "歡迎使用 VueFastMart API"}

@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}