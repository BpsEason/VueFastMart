import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.product import Product
from app.models.user import User
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
import os
import redis.asyncio as redis
from unittest.mock import AsyncMock, patch

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="function")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def admin_user():
    db = TestingSessionLocal()
    hashed_password = pwd_context.hash("securepassword")
    user = User(email="admin@example.com", hashed_password=hashed_password, is_admin=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = jwt.encode(
        {"sub": user.email, "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    db.close()
    return {"user": user, "token": token}

@pytest.fixture
def non_admin_user():
    db = TestingSessionLocal()
    hashed_password = pwd_context.hash("securepassword")
    user = User(email="user@example.com", hashed_password=hashed_password, is_admin=False)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = jwt.encode(
        {"sub": user.email, "exp": datetime.utcnow() + timedelta(minutes=30)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    db.close()
    return {"user": user, "token": token}

@pytest.fixture
def test_products(setup_database):
    db = TestingSessionLocal()
    products = [
        Product(name=f"產品 {i}", description=f"描述 {i}", price=100.0 * i, stock=10 * i)
        for i in range(1, 6)
    ]
    db.add_all(products)
    db.commit()
    db.close()
    return products

def test_create_product_as_admin(setup_database, admin_user):
    response = client.post(
        "/products/",
        json={"name": "測試產品", "description": "這是一個測試產品", "price": 100.0, "stock": 10},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "測試產品"
    assert data["price"] == 100.0

def test_create_product_as_non_admin(setup_database, non_admin_user):
    response = client.post(
        "/products/",
        json={"name": "測試產品", "description": "這是一個測試產品", "price": 100.0, "stock": 10},
        headers={"Authorization": f"Bearer {non_admin_user['token']}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "僅管理員可新增產品"

def test_create_product_invalid_price(setup_database, admin_user):
    response = client.post(
        "/products/",
        json={"name": "測試產品", "description": "這是一個測試產品", "price": -10.0, "stock": 10},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 422
    assert "價格必須大於 0" in response.json()["detail"][0]["msg"]

def test_update_product_as_non_admin(setup_database, admin_user, non_admin_user):
    response = client.post(
        "/products/",
        json={"name": "測試產品", "description": "這是一個測試產品", "price": 100.0, "stock": 10},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    product_id = response.json()["id"]
    
    response = client.put(
        f"/products/{product_id}",
        json={"name": "更新產品", "description": "更新描述", "price": 150.0, "stock": 5},
        headers={"Authorization": f"Bearer {non_admin_user['token']}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "僅管理員可更新產品"

def test_delete_product_as_non_admin(setup_database, admin_user, non_admin_user):
    response = client.post(
        "/products/",
        json={"name": "測試產品", "description": "這是一個測試產品", "price": 100.0, "stock": 10},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    product_id = response.json()["id"]
    
    response = client.delete(
        f"/products/{product_id}",
        headers={"Authorization": f"Bearer {non_admin_user['token']}"}
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "僅管理員可刪除產品"

def test_read_product(setup_database, admin_user):
    client.post(
        "/products/",
        json={"name": "測試產品", "description": "這是一個測試產品", "price": 100.0, "stock": 10},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    response = client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "測試產品"

def test_get_products_pagination(setup_database, test_products):
    response = client.get("/products/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "產品 1"
    assert data[1]["name"] == "產品 2"

    response = client.get("/products/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "產品 3"
    assert data[1]["name"] == "產品 4"

def test_get_products_pagination_out_of_range(setup_database, test_products):
    response = client.get("/products/?skip=10&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_update_product(setup_database, admin_user):
    response = client.post(
        "/products/",
        json={"name": "測試產品", "description": "這是一個測試產品", "price": 100.0, "stock": 10},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    product_id = response.json()["id"]
    
    response = client.put(
        f"/products/{product_id}",
        json={"name": "更新產品", "description": "更新描述", "price": 150.0, "stock": 5},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "更新產品"
    assert data["description"] == "更新描述"
    assert data["price"] == 150.0
    assert data["stock"] == 5

def test_update_nonexistent_product(setup_database, admin_user):
    response = client.put(
        "/products/999",
        json={"name": "更新產品", "description": "更新描述", "price": 150.0, "stock": 5},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "產品不存在"

def test_delete_product(setup_database, admin_user):
    response = client.post(
        "/products/",
        json={"name": "測試產品", "description": "這是一個測試產品", "price": 100.0, "stock": 10},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    product_id = response.json()["id"]
    
    response = client.delete(
        f"/products/{product_id}",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "產品已刪除"

@patch("app.api.products.redis_client")
async def test_delete_product_clears_cache(setup_database, admin_user, mock_redis):
    mock_redis.keys = AsyncMock(return_value=[b"app.api.products:get_products:0:10"])
    mock_redis.delete = AsyncMock()
    response = client.post(
        "/products/",
        json={"name": "測試產品", "description": "這是一個測試產品", "price": 100.0, "stock": 10},
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    product_id = response.json()["id"]
    
    response = client.delete(
        f"/products/{product_id}",
        headers={"Authorization": f"Bearer {admin_user['token']}"}
    )
    assert response.status_code == 200
    mock_redis.keys.assert_called_once_with("app.api.products:get_products:*")
    mock_redis.delete.assert_called_once()