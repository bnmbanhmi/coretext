from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Enum as SAEnum, JSON, Uuid, func
from .database import Base
import uuid
import enum

class ListingStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    RENTED = "RENTED"
    ARCHIVED = "ARCHIVED"

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Integer, nullable=False)
    area_sqm = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    status = Column(SAEnum(ListingStatus), nullable=True, default=ListingStatus.DRAFT)
    attributes = Column(JSON, default={}, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
