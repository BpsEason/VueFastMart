import os
import json

def create_project(project_name):
    project_structure = {
        "backend": {
            "app": {
                "api": {
                    "auth.py": '''from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, User
import os

load_dotenv()

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無效的認證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="電子郵件已被註冊")
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="電子郵件或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
''',
                    "products.py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.product import Product as ProductModel
from app.schemas.product import Product, ProductCreate
from app.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.cache import cache_get, cache_set

router = APIRouter()

async def clear_cache():
    keys = await redis_client.keys("app.api.products:get_products:*")
    if keys:
        await redis_client.delete(*keys)

@router.get("/", response_model=list[Product])
async def get_products(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    cache_key = f"app.api.products:get_products:{skip}:{limit}"
    cached = cache_get(cache_key)
    if cached:
        return json.loads(cached)
    products = db.execute(select(ProductModel).offset(skip).limit(limit)).scalars().all()
    cache_set(cache_key, json.dumps([product.__dict__ for product in products]), timeout=60)
    return products

@router.get("/search", response_model=list[Product])
async def search_products(
    name: str = "",
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = select(ProductModel).filter(ProductModel.name.ilike(f"%{name}%")).offset(skip).limit(limit)
    products = db.execute(query).scalars().all()
    return products

@router.post("/", response_model=Product)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="僅管理員可新增產品")
    db_product = ProductModel(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    await clear_cache()
    return db_product

@router.get("/{product_id}", response_model=Product)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="產品不存在")
    return db_product

@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="僅管理員可更新產品")
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="產品不存在")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    db.refresh(db_product)
    await clear_cache()
    return db_product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="僅管理員可刪除產品")
    db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="產品不存在")
    db.delete(db_product)
    db.commit()
    await clear_cache()
    return {"message": "產品已刪除"}
''',
                    "cart.py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from app.models.cart import CartItem
from app.models.product import Product as ProductModel
from app.schemas.cart import CartItemCreate, CartItem
from app.database import get_db
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=CartItem)
async def add_to_cart(
    cart_item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(ProductModel).filter(ProductModel.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="產品不存在")
    if product.stock < cart_item.quantity:
        raise HTTPException(status_code=400, detail="庫存不足")
    product.stock -= cart_item.quantity
    existing_cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == cart_item.product_id
    ).first()
    if existing_cart_item:
        existing_cart_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_cart_item)
        db.commit()
        return existing_cart_item
    db_cart_item = CartItem(
        user_id=current_user.id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity
    )
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    db.commit()
    return db_cart_item

@router.get("/", response_model=list[CartItem])
async def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).options(selectinload(CartItem.product)).all()
    return cart_items

@router.put("/{cart_item_id}", response_model=CartItem)
async def update_cart_item(
    cart_item_id: int,
    cart_item: CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    if not db_cart_item:
        raise HTTPException(status_code=404, detail="購物車項目不存在")
    product = db.query(ProductModel).filter(ProductModel.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="產品不存在")
    quantity_diff = cart_item.quantity - db_cart_item.quantity
    if product.stock < quantity_diff:
        raise HTTPException(status_code=400, detail="庫存不足")
    product.stock -= quantity_diff
    db_cart_item.quantity = cart_item.quantity
    db.commit()
    db.refresh(db_cart_item)
    db.commit()
    return db_cart_item

@router.delete("/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(
        CartItem.id == cart_item_id,
        CartItem.user_id == current_user.id
    ).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="購物車項目不存在")
    product = db.query(ProductModel).filter(ProductModel.id == cart_item.product_id).first()
    product.stock += cart_item.quantity
    db.delete(cart_item)
    db.commit()
    return {"message": "已移除購物車項目"}
''',
                },
                "models": {
                    "user.py": '''from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
''',
                    "product.py": '''from sqlalchemy import Column, Integer, String, Float, Text, Index, CheckConstraint
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)
    image_url = Column(String, nullable=True)

    __table_args__ = (
        Index('idx_name', 'name'),
        CheckConstraint('price > 0', name='positive_price'),
        CheckConstraint('stock >= 0', name='non_negative_stock'),
    )
''',
                    "cart.py": '''from sqlalchemy import Column, Integer, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)

    user = relationship("User")
    product = relationship("Product")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='positive_quantity'),
        Index('idx_user_product', 'user_id', 'product_id', unique=True),
    )
''',
                },
                "schemas": {
                    "user.py": '''from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("密碼需至少 8 個字符")
        if not re.search(r"[A-Za-z]", v) or not re.search(r"\d", v):
            raise ValueError("密碼需包含字母和數字")
        return v

class User(BaseModel):
    id: int
    email: EmailStr
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True
''',
                    "product.py": '''from pydantic import BaseModel, validator
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: Optional[str]
    price: float
    stock: int
    image_url: Optional[str]

    @validator("price")
    def price_positive(cls, v):
        if v <= 0:
            raise ValueError("價格必須大於 0")
        return v

    @validator("stock")
    def stock_non_negative(cls, v):
        if v < 0:
            raise ValueError("庫存不能為負")
        return v

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True
''',
                    "cart.py": '''from pydantic import BaseModel, validator
from .product import Product

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int

    @validator("quantity")
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("數量必須大於 0")
        return v

class CartItem(CartItemCreate):
    id: int
    product: Product

    class Config:
        from_attributes = True
''',
                },
                "database.py": '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vuefastmart.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
                "cache.py": '''import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

def cache_get(key: str):
    return redis_client.get(key)

def cache_set(key: str, value: str, timeout: int = 3600):
    redis_client.setex(key, timeout, value)
''',
                "main.py": '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import auth, products, cart
from app.database import engine, Base
from sqlalchemy import inspect
import os

load_dotenv()

if not os.getenv("FRONTEND_URL"):
    raise ValueError("FRONTEND_URL environment variable is not set")

app = FastAPI(title="VueFastMart API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def check_database_connection():
    try:
        with engine.connect() as connection:
            inspect(engine).get_table_names()
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {str(e)}")

check_database_connection()
Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/auth", tags=["認證"])
app.include_router(products.router, prefix="/api/products", tags=["產品"])
app.include_router(cart.router, prefix="/api/cart", tags=["購物車"])

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
''',
                "tests": {
                    "test_auth.py": '''import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.api.auth import get_password_hash

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "Secure123"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_login_user():
    db = TestingSessionLocal()
    hashed_password = get_password_hash("Secure123")
    db.add(User(email="test@example.com", hashed_password=hashed_password))
    db.commit()
    db.close()
    response = client.post(
        "/api/auth/token",
        data={"username": "test@example.com", "password": "Secure123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
''',
                    "test_products.py": '''import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.product import Product
from app.models.user import User
from app.api.auth import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def admin_token():
    db = TestingSessionLocal()
    hashed_password = get_password_hash("Secure123")
    db.add(User(email="admin@example.com", hashed_password=hashed_password, is_admin=True))
    db.commit()
    db.close()
    return create_access_token({"sub": "admin@example.com"})

def test_get_products():
    db = TestingSessionLocal()
    db.add(Product(name="Test Product", price=10.0, stock=100))
    db.commit()
    db.close()
    response = client.get("/api/products/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_create_product(admin_token):
    response = client.post(
        "/api/products/",
        json={"name": "New Product", "description": "Test", "price": 20.0, "stock": 50},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Product"
''',
                    "test_cart.py": '''import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.product import Product
from app.api.auth import get_password_hash, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def user_token():
    db = TestingSessionLocal()
    hashed_password = get_password_hash("Secure123")
    db.add(User(email="test@example.com", hashed_password=hashed_password))
    db.commit()
    db.close()
    return create_access_token({"sub": "test@example.com"})

@pytest.fixture
def product():
    db = TestingSessionLocal()
    db_product = Product(name="Test Product", price=10.0, stock=100)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    db.close()
    return db_product

def test_add_to_cart(user_token, product):
    response = client.post(
        "/api/cart/",
        json={"product_id": product.id, "quantity": 2},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["quantity"] == 2

def test_get_cart(user_token):
    response = client.get(
        "/api/cart/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
''',
                },
                "requirements.txt": '''fastapi==0.115.0
uvicorn==0.32.0
sqlalchemy==2.0.35
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
redis==5.1.1
pytest==8.3.3
pytest-cov==5.0.0
httpx==0.27.2
psycopg2-binary==2.9.10
''',
                ".env.example": '''DATABASE_URL=sqlite:///./vuefastmart.db
SECRET_KEY=your-secret-key-here
FRONTEND_URL=http://localhost:5173
REDIS_HOST=localhost
REDIS_PORT=6379
''',
            },
            "Dockerfile": '''FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''',
            "docker-compose.yml": '''version: '3.8'
services:
  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./vuefastmart.db
      - SECRET_KEY=${SECRET_KEY}
      - FRONTEND_URL=http://localhost:5173
    volumes:
      - ./backend:/app
  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"
''',
        },
        "frontend": {
            "src": {
                "components": {
                    "ProductCard.vue": '''<template>
  <div class="border rounded-lg p-4 shadow-md">
    <img :src="product.image_url || 'https://via.placeholder.com/150'" alt="Product" class="w-full h-48 object-cover mb-2">
    <h3 class="text-lg font-semibold">{{ product.name }}</h3>
    <p class="text-gray-600">{{ product.description }}</p>
    <p class="text-xl font-bold">${{ product.price.toFixed(2) }}</p>
    <p class="text-sm">庫存: {{ product.stock }}</p>
    <button @click="addToCart" class="mt-2 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
      加入購物車
    </button>
  </div>
</template>

<script>
import { addToCart } from '../utils/cart.js';

export default {
  props: {
    product: {
      type: Object,
      required: true
    }
  },
  methods: {
    async addToCart() {
      try {
        await addToCart(this.product.id, 1);
        alert('已加入購物車');
      } catch (error) {
        console.error('加入購物車失敗:', error);
        alert('加入購物車失敗');
      }
    }
  }
}
</script>
''',
                    "ProductList.vue": '''<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    <ProductCard v-for="product in products" :key="product.id" :product="product" />
  </div>
</template>

<script>
import ProductCard from './ProductCard.vue';
import axios from 'axios';

export default {
  components: { ProductCard },
  data() {
    return {
      products: []
    };
  },
  async created() {
    try {
      const response = await axios.get('/api/products/');
      this.products = response.data;
    } catch (error) {
      console.error('獲取產品失敗:', error);
    }
  }
}
</script>
''',
                    "ProductDetail.vue": '''<template>
  <div v-if="product" class="max-w-2xl mx-auto p-4">
    <img :src="product.image_url || 'https://via.placeholder.com/300'" alt="Product" class="w-full h-96 object-cover mb-4">
    <h1 class="text-2xl font-bold">{{ product.name }}</h1>
    <p class="text-gray-600">{{ product.description }}</p>
    <p class="text-xl font-bold">${{ product.price.toFixed(2) }}</p>
    <p class="text-sm">庫存: {{ product.stock }}</p>
    <button @click="addToCart" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
      加入購物車
    </button>
  </div>
</template>

<script>
import { addToCart } from '../utils/cart.js';
import axios from 'axios';

export default {
  data() {
    return {
      product: null
    };
  },
  async created() {
    try {
      const response = await axios.get(`/api/products/${this.$route.params.id}`);
      this.product = response.data;
    } catch (error) {
      console.error('獲取產品詳情失敗:', error);
    }
  },
  methods: {
    async addToCart() {
      try {
        await addToCart(this.product.id, 1);
        alert('已加入購物車');
      } catch (error) {
        console.error('加入購物車失敗:', error);
        alert('加入購物車失敗');
      }
    }
  }
}
</script>
''',
                    "Cart.vue": '''<template>
  <div class="p-4">
    <h1 class="text-2xl font-bold mb-4">購物車</h1>
    <div v-if="cartItems.length === 0" class="text-gray-600">購物車為空</div>
    <div v-else>
      <div v-for="item in cartItems" :key="item.id" class="border-b py-2 flex justify-between items-center">
        <div>
          <p class="font-semibold">{{ item.product.name }}</p>
          <p class="text-gray-600">${{ item.product.price.toFixed(2) }} x {{ item.quantity }}</p>
        </div>
        <div class="flex items-center space-x-2">
          <input
            type="number"
            v-model.number="item.quantity"
            @change="updateQuantity(item)"
            min="1"
            class="w-16 border rounded px-2 py-1"
          >
          <button @click="removeItem(item.id)" class="text-red-500 hover:text-red-700">移除</button>
        </div>
      </div>
      <p class="mt-4 text-xl font-bold">總計: ${{ totalPrice.toFixed(2) }}</p>
    </div>
  </div>
</template>

<script>
import { getCart, removeFromCart, updateCartItem } from '../utils/cart.js';

export default {
  data() {
    return {
      cartItems: []
    };
  },
  computed: {
    totalPrice() {
      return this.cartItems.reduce((total, item) => total + item.product.price * item.quantity, 0);
    }
  },
  async created() {
    await this.loadCart();
  },
  methods: {
    async loadCart() {
      try {
        this.cartItems = await getCart();
      } catch (error) {
        console.error('獲取購物車失敗:', error);
      }
    },
    async updateQuantity(item) {
      try {
        await updateCartItem(item.id, item.product.id, item.quantity);
        await this.loadCart();
      } catch (error) {
        console.error('更新數量失敗:', error);
        alert('更新數量失敗');
      }
    },
    async removeItem(itemId) {
      try {
        await removeFromCart(itemId);
        await this.loadCart();
      } catch (error) {
        console.error('移除項目失敗:', error);
        alert('移除項目失敗');
      }
    }
  }
}
</script>
''',
                    "Register.vue": '''<template>
  <div class="max-w-md mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">註冊</h1>
    <form @submit.prevent="register">
      <div class="mb-4">
        <label for="email" class="block text-sm font-medium">電子郵件</label>
        <input v-model="form.email" type="email" id="email" class="w-full border rounded px-2 py-1" required>
      </div>
      <div class="mb-4">
        <label for="password" class="block text-sm font-medium">密碼</label>
        <input v-model="form.password" type="password" id="password" class="w-full border rounded px-2 py-1" required>
      </div>
      <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">註冊</button>
      <p v-if="error" class="text-red-500 mt-2">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      error: ''
    };
  },
  methods: {
    async register() {
      try {
        await axios.post('/api/auth/register', this.form);
        this.$router.push('/login');
      } catch (error) {
        this.error = error.response?.data?.detail || '註冊失敗，請確保密碼包含字母和數字';
      }
    }
  }
}
</script>
''',
                    "Login.vue": '''<template>
  <div class="max-w-md mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">登入</h1>
    <form @submit.prevent="login">
      <div class="mb-4">
        <label for="email" class="block text-sm font-medium">電子郵件</label>
        <input v-model="form.email" type="email" id="email" class="w-full border rounded px-2 py-1" required>
      </div>
      <div class="mb-4">
        <label for="password" class="block text-sm font-medium">密碼</label>
        <input v-model="form.password" type="password" id="password" class="w-full border rounded px-2 py-1" required>
      </div>
      <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">登入</button>
      <p v-if="error" class="text-red-500 mt-2">{{ error }}</p>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      error: ''
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('/api/auth/token', new URLSearchParams({
          username: this.form.email,
          password: this.form.password
        }));
        localStorage.setItem('token', response.data.access_token);
        this.$router.push('/');
      } catch (error) {
        this.error = error.response?.data?.detail || '登入失敗';
      }
    }
  }
}
</script>
''',
                },
                "utils": {
                    "cart.js": '''import axios from 'axios';

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export async function addToCart(productId, quantity) {
  const response = await axios.post('/api/cart/', { product_id: productId, quantity }, {
    headers: getAuthHeaders()
  });
  return response.data;
}

export async function getCart() {
  const response = await axios.get('/api/cart/', {
    headers: getAuthHeaders()
  });
  return response.data;
}

export async function updateCartItem(cartItemId, productId, quantity) {
  const response = await axios.put(`/api/cart/${cartItemId}`, { product_id: productId, quantity }, {
    headers: getAuthHeaders()
  });
  return response.data;
}

export async function removeFromCart(cartItemId) {
  const response = await axios.delete(`/api/cart/${cartItemId}`, {
    headers: getAuthHeaders()
  });
  return response.data;
}
'''
                },
                "App.vue": '''<template>
  <div>
    <nav class="bg-gray-800 text-white p-4">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        <router-link to="/" class="text-xl font-bold">VueFastMart</router-link>
        <div class="space-x-4">
          <router-link to="/">首頁</router-link>
          <router-link to="/cart">購物車</router-link>
          <router-link v-if="!isLoggedIn" to="/login">登入</router-link>
          <router-link v-if="!isLoggedIn" to="/register">註冊</router-link>
          <button v-if="isLoggedIn" @click="logout" class="text-white">登出</button>
        </div>
      </div>
    </nav>
    <router-view class="p-4" />
  </div>
</template>

<script>
export default {
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token');
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    }
  }
}
</script>
''',
                "main.js": '''import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

const app = createApp(App);
app.use(router);
app.mount('#app');
''',
                "router.js": '''import { createRouter, createWebHistory } from 'vue-router';
import ProductList from './components/ProductList.vue';
import ProductDetail from './components/ProductDetail.vue';
import Cart from './components/Cart.vue';
import Register from './components/Register.vue';
import Login from './components/Login.vue';

const routes = [
  { path: '/', component: ProductList },
  { path: '/products/:id', component: ProductDetail },
  { path: '/cart', component: Cart },
  { path: '/register', component: Register },
  { path: '/login', component: Login }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

router.beforeEach((to, from, next) => {
  const publicPages = ['/login', '/register', '/', '/products/:id'];
  const authRequired = !publicPages.includes(to.path);
  const loggedIn = localStorage.getItem('token');

  if (authRequired && !loggedIn) {
    next('/login');
  } else {
    next();
  }
});

export default router;
''',
            },
            "tests": {
                "ProductList.test.js": '''import { mount } from '@vue/test-utils';
import ProductList from '../src/components/ProductList.vue';
import axios from 'axios';

jest.mock('axios');

describe('ProductList.vue', () => {
  it('fetches and displays products', async () => {
    const products = [
      { id: 1, name: 'Test Product', price: 10, stock: 100 }
    ];
    axios.get.mockResolvedValue({ data: products });

    const wrapper = mount(ProductList);
    await wrapper.vm.$nextTick();

    expect(axios.get).toHaveBeenCalledWith('/api/products/');
    await wrapper.vm.$nextTick();
    expect(wrapper.vm.products).toEqual(products);
  });
});
''',
                "Cart.test.js": '''import { mount } from '@vue/test-utils';
import Cart from '../src/components/Cart.vue';
import { getCart } from '../src/utils/cart.js';

jest.mock('../src/utils/cart.js');

describe('Cart.vue', () => {
  it('displays cart items', async () => {
    const cartItems = [
      { id: 1, product: { name: 'Test Product', price: 10 }, quantity: 2 }
    ];
    getCart.mockResolvedValue(cartItems);

    const wrapper = mount(Cart);
    await wrapper.vm.$nextTick();

    expect(getCart).toHaveBeenCalled();
    expect(wrapper.vm.cartItems).toEqual(cartItems);
    expect(wrapper.text()).toContain('Test Product');
  });
});
''',
            },
            "package.json": '''{
  "name": "vuefastmart-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "jest"
  },
  "dependencies": {
    "vue": "^3.5.12",
    "vue-router": "^4.4.5",
    "axios": "^1.7.7"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.4",
    "vite": "^5.4.8",
    "jest": "^29.7.0",
    "@vue/test-utils": "^2.4.6",
    "vue-jest": "^5.0.0-alpha.10"
  }
}
''',
            "vite.config.js": '''import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});
''',
            ".env.example": '''VITE_API_URL=http://localhost:8000
'''
        },
        "README.md": '''# VueFastMart

一個使用 Vue.js 和 FastAPI 構建的電子商務平台。

## 功能
- 用戶註冊與登入
- 產品瀏覽與搜索
- 購物車管理
- 管理員產品管理

## 技術棧
- 前端: Vue.js 3, Vue Router, Axios
- 後端: FastAPI, SQLAlchemy, Redis
- 資料庫: SQLite (開發), PostgreSQL (生產)
- 測試: Pytest, Jest

## 安裝

### 先決條件
- Node.js >= 18
- Python >= 3.12
- Redis

### 後端設置
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 編輯 .env 設置 SECRET_KEY
openssl rand -hex 32
uvicorn app.main:app --reload
```

### 前端設置
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### 使用 Docker
```bash
docker-compose up -d
```

## 測試
```bash
# 後端
cd backend
pytest tests/ --cov=app --cov-report=html

# 前端
cd frontend
npm run test
```

## API 文檔
- 訪問 `http://localhost:8000/docs` 查看 Swagger UI

## 部署
- 使用 PostgreSQL 替代 SQLite
- 配置環境變數
- 使用 Gunicorn 運行 FastAPI
- 使用 Nginx 作為反向代理
'''
    }

    def create_file(path, content):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def create_directory_structure(base_path, structure):
        for name, item in structure.items():
            path = os.path.join(base_path, name)
            if isinstance(item, dict):
                create_directory_structure(path, item)
            else:
                create_file(path, item)

    project_path = os.path.join(os.getcwd(), project_name)
    create_directory_structure(project_path, project_structure)
    print(f"Project {project_name} created successfully at {project_path}")

if __name__ == "__main__":
    create_project("VueFastMart")