from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from typing import Any
from .. import schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)

@router.post("", response_model=schemas.ListingResponse, status_code=status.HTTP_201_CREATED)
def create_listing(listing: schemas.ListingCreate, db: Session = Depends(get_db)) -> Any:
    try:
        db_listing = models.Listing(
            title=listing.title,
            price=listing.price,
            area_sqm=listing.area,
            address=listing.address,
            status=models.ListingStatus.DRAFT # Default status
        )
        db.add(db_listing)
        db.commit()
        db.refresh(db_listing)
        return db_listing
    except OperationalError:
        # Catch DB connection errors
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System is currently busy, please try again later"
        )
    except Exception as e:
        # Generic fallback
        print(f"Error creating listing: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
