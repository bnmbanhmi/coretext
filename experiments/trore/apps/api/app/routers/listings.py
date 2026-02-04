from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import or_
from typing import Any
from uuid import UUID
from .. import schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)

@router.get("/{id}", response_model=schemas.ListingResponse)
def get_listing(id: UUID, db: Session = Depends(get_db)) -> Any:
    listing = db.query(models.Listing).filter(models.Listing.id == id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@router.get("", response_model=list[schemas.ListingResponse])
def get_listings(
    skip: int = 0,
    limit: int = 20,
    q: str | None = None,
    db: Session = Depends(get_db)
) -> Any:
    query = db.query(models.Listing).filter(models.Listing.status == models.ListingStatus.AVAILABLE)
    
    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                models.Listing.title.ilike(search),
                models.Listing.description.ilike(search)
            )
        )
    
    # Sort by created_at desc
    query = query.order_by(models.Listing.created_at.desc())
    
    listings = query.offset(skip).limit(limit).all()
    return listings

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
