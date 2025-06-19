from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import auth, products, cart
from app.database import engine, Base
import os

load_dotenv()

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
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["認證"])
app.include_router(products.router, prefix="/products", tags=["產品"])
app.include_router(cart.router, prefix="/cart", tags=["購物車"])

@app.get("/")
def read_root():
    return {"message": "歡迎使用 VueFastMart API"}