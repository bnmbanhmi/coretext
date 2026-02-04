from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class ListingStatus(str, Enum):
    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    RENTED = "RENTED"
    ARCHIVED = "ARCHIVED"

class ListingBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: int = Field(..., gt=0)
    area: float = Field(..., gt=0, alias="area_sqm") # Use alias to map API 'area' to DB 'area_sqm' if needed, or just handle manually. 
    # Actually, Pydantic alias is for input parsing. If I want input "area", I use alias="area".
    # But usually it's cleaner to match DB or use a mapper. 
    # Let's use `area` as the field name in Pydantic and map it to `area_sqm` when creating DB model.
    # So: area: float = Field(..., gt=0)
    address: str

class ListingCreate(BaseModel):
    title: str
    price: int = Field(..., gt=0)
    area: float = Field(..., gt=0) # Client sends "area"
    address: str

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = Field(None, gt=0)
    area: Optional[float] = Field(None, gt=0)
    address: Optional[str] = None
    status: Optional[ListingStatus] = None
    attributes: Optional[dict] = None

class ListingResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    price: int
    area_sqm: float
    address: str
    attributes: Optional[dict] = {}
    status: Optional[ListingStatus] = None
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
