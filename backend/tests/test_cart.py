import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.models.product import Product
from app.models.cart import CartItem
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secure-secret-key")
ALGORITHM = "HS256"

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    db = TestingSessionLocal()
    hashed_password = pwd_context.hash("securepassword")
    user = User(email="test@example.com", hashed_password=hashed_password)
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
def test_product():
    db = TestingSessionLocal()
    product = Product(name="測試產品", description="這是一個測試產品", price=100.0, stock=10)
    db.add(product)
    db.commit()
    db.refresh(product)
    db.close()
    return product

def test_add_to_cart(setup_database, test_user, test_product):
    response = client.post(
        "/cart/",
        json={"product_id": test_product.id, "quantity": 2},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["product_id"] == test_product.id
    assert data["quantity"] == 2
    assert data["product"]["name"] == "測試產品"

def test_add_to_cart_insufficient_stock(setup_database, test_user, test_product):
    response = client.post(
        "/cart/",
        json={"product_id": test_product.id, "quantity": 20},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "庫存不足"

def test_get_cart(setup_database, test_user, test_product):
    # 先添加一個購物車項目
    client.post(
        "/cart/",
        json={"product_id": test_product.id, "quantity": 1},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    response = client.get(
        "/cart/",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["product_id"] == test_product.id
    assert data[0]["quantity"] == 1

def test_remove_from_cart(setup_database, test_user, test_product):
    # 先添加一個購物車項目
    response = client.post(
        "/cart/",
        json={"product_id": test_product.id, "quantity": 1},
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    cart_item_id = response.json()["id"]
    
    response = client.delete(
        f"/cart/{cart_item_id}",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "已移除購物車項目"

def test_remove_nonexistent_cart_item(setup_database, test_user):
    response = client.delete(
        "/cart/999",
        headers={"Authorization": f"Bearer {test_user['token']}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "購物車項目不存在"