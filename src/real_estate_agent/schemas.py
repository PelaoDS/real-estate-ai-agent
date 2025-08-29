"""Data models and schemas for real estate properties (MVP version)."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class PropertyType(str, Enum):
    """Enum for property types."""
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    STUDIO = "studio"


class PropertyStatus(str, Enum):
    """Enum for property listing status."""
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"


class Amenity(str, Enum):
    """Common property amenities."""
    POOL = "pool"
    GYM = "gym"
    PARKING = "parking"
    PET_FRIENDLY = "pet_friendly"
    BALCONY = "balcony"
    FIREPLACE = "fireplace"
    DISHWASHER = "dishwasher"
    WASHER_DRYER = "washer_dryer"
    AIR_CONDITIONING = "air_conditioning"
    HARDWOOD_FLOORS = "hardwood_floors"


class PropertyMetadata(BaseModel):
    """Simple metadata for property filtering and search (MVP)."""
    
    # Identification
    property_id: str = Field(..., description="Unique property identifier")
    
    # Basic Property Info
    property_type: PropertyType = Field(..., description="Type of property")
    status: PropertyStatus = Field(default=PropertyStatus.ACTIVE, description="Listing status")
    price: int = Field(..., gt=0, description="Property price in USD")
    bedrooms: int = Field(..., ge=0, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=0, description="Number of bathrooms")
    square_feet: int = Field(..., gt=0, description="Property size in square feet")
    
    # Location (simplified)
    city: str = Field(..., description="City")
    state: str = Field(..., max_length=2, description="State abbreviation (e.g., 'NY')")
    neighborhood: Optional[str] = Field(None, description="Neighborhood name")
    
    # Property Details
    year_built: Optional[int] = Field(None, ge=1800, le=2030, description="Year property was built")
    
    # Amenities
    amenities: List[Amenity] = Field(default_factory=list, description="Property amenities")
    
    # Market Information
    days_on_market: int = Field(default=0, ge=0, description="Number of days on market")
    listing_agent: str = Field(..., description="Name of listing agent")
    
    @validator('state')
    def validate_state(cls, v):
        """Ensure state is uppercase."""
        return v.upper() if v else v
    
    @property
    def price_per_sqft(self) -> float:
        """Calculate price per square foot."""
        return self.price / self.square_feet if self.square_feet > 0 else 0


class PropertyListing(BaseModel):
    """Complete property listing with description and metadata (MVP)."""
    
    # Core content for semantic search - ONLY description will be vectorized
    title: str = Field(..., description="Property listing title")
    description: str = Field(..., description="Detailed property description for vectorization")
    
    # Structured metadata for filtering
    metadata: PropertyMetadata = Field(..., description="Property metadata for filtering")
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    
    def to_dict_for_pinecone(self) -> dict:
        """Convert to dictionary format suitable for Pinecone."""
        return {
            "id": self.metadata.property_id,
            "values": [],  # Will be populated with embeddings from description only
            "metadata": {
                # Core searchable fields - only description is vectorized
                "title": self.title,
                "description": self.description,  # This is what gets vectorized
                
                # Filterable metadata
                "property_type": self.metadata.property_type.value,
                "status": self.metadata.status.value,
                "price": self.metadata.price,
                "bedrooms": self.metadata.bedrooms,
                "bathrooms": self.metadata.bathrooms,
                "square_feet": self.metadata.square_feet,
                "city": self.metadata.city,
                "state": self.metadata.state,
                "neighborhood": self.metadata.neighborhood,
                "year_built": self.metadata.year_built,
                "days_on_market": self.metadata.days_on_market,
                "amenities": [amenity.value for amenity in self.metadata.amenities],
                "listing_agent": self.metadata.listing_agent,
                
                # Calculated fields
                "price_per_sqft": self.metadata.price_per_sqft,
                
                # System fields
                "created_at": self.created_at.isoformat(),
            }
        }


class SearchQuery(BaseModel):
    """User search query with filters and preferences (MVP)."""
    
    # Raw user query
    query: str = Field(..., description="Natural language search query")
    
    # Extracted filters (will be populated by agent)
    filters: Dict[str, Any] = Field(default_factory=dict, description="Extracted metadata filters")
    
    # Search preferences
    max_results: int = Field(default=10, ge=1, le=50, description="Maximum number of results")
    
    # Budget constraints
    min_price: Optional[int] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[int] = Field(None, ge=0, description="Maximum price")
    
    # Property requirements
    min_bedrooms: Optional[int] = Field(None, ge=0, description="Minimum bedrooms")
    min_bathrooms: Optional[float] = Field(None, ge=0, description="Minimum bathrooms")
    required_amenities: List[Amenity] = Field(default_factory=list, description="Required amenities")
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        """Ensure max_price is greater than min_price if both are provided."""
        min_price = values.get('min_price')
        if min_price is not None and v is not None and v <= min_price:
            raise ValueError('max_price must be greater than min_price')
        return v