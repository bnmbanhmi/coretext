from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.listings import ListingStatus

class ListingBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: int = Field(..., gt=0, description="Price must be a positive integer")
    area_sqm: float = Field(..., gt=0, description="Area in square meters")
    address: str = Field(..., min_length=1)
    status: ListingStatus = ListingStatus.DRAFT
    attributes: Dict[str, Any] = Field(default_factory=dict)

class ListingCreate(ListingBase):
    pass

class ListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[int] = Field(None, gt=0)
    area_sqm: Optional[float] = Field(None, gt=0)
    address: Optional[str] = Field(None, min_length=1)
    status: Optional[ListingStatus] = None
    attributes: Optional[Dict[str, Any]] = None

class Listing(ListingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)