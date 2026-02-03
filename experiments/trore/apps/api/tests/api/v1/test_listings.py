from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Setup in-memory SQLite DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def setup_module(module):
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    Base.metadata.drop_all(bind=engine)

def test_create_listing_success():
    response = client.post(
        "/api/v1/listings/",
        json={
            "title": "Sunny Studio in D1",
            "description": "A nice place",
            "price": 5000000,
            "area_sqm": 30.0,
            "address": "123 Le Loi"
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Sunny Studio in D1"
    assert data["price"] == 5000000
    assert "id" in data
    assert data["status"] == "DRAFT"

def test_create_listing_validation_error_negative_price():
    response = client.post(
        "/api/v1/listings/",
        json={
            "title": "Cheap place",
            "price": -100,
            "area_sqm": 30.0,
            "address": "123 Le Loi"
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    # Pydantic v2 error structure check might be needed, but checking 422 is good start

def test_create_listing_validation_error_missing_fields():
    response = client.post(
        "/api/v1/listings/",
        json={
            "title": "Missing info"
        },
    )
    assert response.status_code == 422
