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

def test_get_listings_pagination_and_filtering():
    # Setup data
    # Create 15 AVAILABLE listings
    for i in range(15):
        client.post(
            "/api/v1/listings/",
            json={
                "title": f"Available {i}",
                "price": 1000000 * (i + 1),
                "area_sqm": 20.0 + i,
                "address": f"Street {i}",
                "status": "AVAILABLE"
            },
        )
    
    # Create 5 RENTED listings
    for i in range(5):
        client.post(
            "/api/v1/listings/",
            json={
                "title": f"Rented {i}",
                "price": 2000000,
                "area_sqm": 30.0,
                "address": "Rented St",
                "status": "RENTED"
            },
        )

    # Test 1: Default params (status=AVAILABLE, limit=20, skip=0)
    # Note: DB might retain data from previous tests, so we filter strictly or rely on known count
    # Since it's in-memory static pool, previous tests ran.
    # test_create_listing_success created 1 DRAFT.
    
    response = client.get("/api/v1/listings/")
    assert response.status_code == 200
    data = response.json()
    
    # We expect only AVAILABLE listings.
    # There are 15 created here.
    assert len(data) == 15
    for item in data:
        assert item["status"] == "AVAILABLE"

    # Test 2: Pagination (limit=5)
    response = client.get("/api/v1/listings/?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

    # Test 3: Pagination (skip=10)
    response = client.get("/api/v1/listings/?skip=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5  # 15 total - 10 skipped = 5 left

    # Test 4: Filter by RENTED
    response = client.get("/api/v1/listings/?status=RENTED")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    for item in data:
        assert item["status"] == "RENTED"

def test_get_listing_by_id_success():
    # Create a listing
    create_response = client.post(
        "/api/v1/listings/",
        json={
            "title": "Specific Listing",
            "price": 123456,
            "area_sqm": 50.0,
            "address": "Specific St",
            "attributes": {"wifi": True, "pets": False}
        },
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    # Get the listing
    response = client.get(f"/api/v1/listings/{created_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_id
    assert data["title"] == "Specific Listing"
    assert data["attributes"] == {"wifi": True, "pets": False}

def test_get_listing_by_id_not_found():
    # Use a random UUID that likely doesn't exist
    import uuid
    random_uuid = str(uuid.uuid4())
    response = client.get(f"/api/v1/listings/{random_uuid}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Listing not found"

def test_get_listing_by_id_invalid_uuid():
    response = client.get("/api/v1/listings/not-a-uuid")
    assert response.status_code == 422