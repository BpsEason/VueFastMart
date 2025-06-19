import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User
from passlib.context import CryptContext

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

def test_register_user(setup_database):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_admin"] is False

def test_register_duplicate_email(setup_database):
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepassword"}
    )
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "anotherpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "電子郵件已被註冊"

def test_login_success(setup_database):
    # 先註冊用戶
    hashed_password = pwd_context.hash("securepassword")
    db = TestingSessionLocal()
    user = User(email="test@example.com", hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.close()

    response = client.post(
        "/auth/token",
        data={"username": "test@example.com", "password": "securepassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(setup_database):
    response = client.post(
        "/auth/token",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "電子郵件或密碼錯誤"