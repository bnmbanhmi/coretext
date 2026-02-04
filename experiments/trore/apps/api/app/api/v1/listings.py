from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.listing import Listing, ListingCreate
from app.models.listings import Listing as ListingModel, ListingStatus

router = APIRouter()

@router.get("/{id}", response_model=Listing)
def get_listing(id: UUID, db: Session = Depends(get_db)):
    listing = db.query(ListingModel).filter(ListingModel.id == id).first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return listing

@router.get("/", response_model=List[Listing])
def get_listings(
    skip: int = 0,
    limit: int = 20,
    status: Optional[ListingStatus] = Query(default=ListingStatus.AVAILABLE),
    db: Session = Depends(get_db)
):
    query = db.query(ListingModel)
    
    if status:
        query = query.filter(ListingModel.status == status)
        
    listings = query.offset(skip).limit(limit).all()
    return listings

@router.post("/", response_model=Listing, status_code=status.HTTP_201_CREATED)
def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    db_listing = ListingModel(
        title=listing.title,
        description=listing.description,
        price=listing.price,
        area_sqm=listing.area_sqm,
        address=listing.address,
        status=listing.status,
        attributes=listing.attributes
    )
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing
