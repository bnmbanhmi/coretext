from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
import pytest

# Setup Test DB
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

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_listing_success():
    payload = {
        "title": "Sunny Studio",
        "price": 5000000,
        "area": 30,
        "address": "123 Le Loi"
    }
    response = client.post("/listings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Sunny Studio"
    assert "id" in data
    assert data["area_sqm"] == 30

def test_create_listing_negative_price():
    payload = {
        "title": "Sunny Studio",
        "price": -100,
        "area": 30,
        "address": "123 Le Loi"
    }
    response = client.post("/listings", json=payload)
    assert response.status_code == 422

def test_create_listing_negative_area():
    payload = {
        "title": "Sunny Studio",
        "price": 5000000,
        "area": -5,
        "address": "123 Le Loi"
    }
    response = client.post("/listings", json=payload)
    assert response.status_code == 422

def test_get_listings_defaults():
    db = TestingSessionLocal()
    from app.models import Listing, ListingStatus
    
    l1 = Listing(title="Avail 1", price=100, area_sqm=10, address="A1", status=ListingStatus.AVAILABLE)
    l2 = Listing(title="Draft 1", price=100, area_sqm=10, address="A2", status=ListingStatus.DRAFT)
    db.add(l1)
    db.add(l2)
    db.commit()
    db.close()

    response = client.get("/listings")
    assert response.status_code == 200 
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Avail 1"

def test_get_listings_search():
    db = TestingSessionLocal()
    from app.models import Listing, ListingStatus
    
    l1 = Listing(title="Sunny Studio", description="Bright", price=100, area_sqm=10, address="A1", status=ListingStatus.AVAILABLE)
    l2 = Listing(title="Dark Cave", description="Dim", price=100, area_sqm=10, address="A2", status=ListingStatus.AVAILABLE)
    db.add(l1)
    db.add(l2)
    db.commit()
    db.close()

    response = client.get("/listings?q=Sunny")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Sunny Studio"

    response = client.get("/listings?q=Dim")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Dark Cave"

def test_get_listings_pagination():
    db = TestingSessionLocal()
    from app.models import Listing, ListingStatus
    
    for i in range(25):
        db.add(Listing(title=f"L{i}", price=100, area_sqm=10, address="A", status=ListingStatus.AVAILABLE))
    db.commit()
    db.close()

    response = client.get("/listings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 20

    response = client.get("/listings?skip=20")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5