from sqlalchemy import Column, String, Integer, Float, Text, Enum, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.db.base import Base

class ListingStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    RENTED = "RENTED"
    ARCHIVED = "ARCHIVED"

class Listing(Base):
    __tablename__ = "listings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Integer, nullable=False)
    area_sqm = Column(Float, nullable=False)
    address = Column(String, nullable=False)
    status = Column(Enum(ListingStatus), default=ListingStatus.DRAFT)
    attributes = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
