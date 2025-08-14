"""Data models and schemas for real estate properties."""

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
    DUPLEX = "duplex"
    STUDIO = "studio"
    LAND = "land"
    COMMERCIAL = "commercial"


class PropertyStatus(str, Enum):
    """Enum for property listing status."""
    ACTIVE = "active"
    PENDING = "pending"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


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
    UPDATED_KITCHEN = "updated_kitchen"
    WALK_IN_CLOSET = "walk_in_closet"
    DOORMAN = "doorman"
    ELEVATOR = "elevator"
    ROOF_DECK = "roof_deck"


class PropertyMetadata(BaseModel):
    """Metadata for property filtering and search."""
    
    # Identification
    property_id: str = Field(..., description="Unique property identifier")
    mls_number: Optional[str] = Field(None, description="MLS listing number")
    
    # Basic Property Info
    property_type: PropertyType = Field(..., description="Type of property")
    status: PropertyStatus = Field(default=PropertyStatus.ACTIVE, description="Listing status")
    price: int = Field(..., gt=0, description="Property price in USD")
    bedrooms: int = Field(..., ge=0, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=0, description="Number of bathrooms")
    square_feet: int = Field(..., gt=0, description="Property size in square feet")
    
    # Location
    address: str = Field(..., description="Full street address")
    neighborhood: str = Field(..., description="Neighborhood name")
    city: str = Field(..., description="City")
    state: str = Field(..., max_length=2, description="State abbreviation (e.g., 'NY')")
    zip_code: str = Field(..., description="ZIP code")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    
    # Property Details
    year_built: Optional[int] = Field(None, ge=1800, le=2030, description="Year property was built")
    lot_size: Optional[int] = Field(None, ge=0, description="Lot size in square feet")
    garage_spaces: int = Field(default=0, ge=0, description="Number of garage spaces")
    parking_spaces: int = Field(default=0, ge=0, description="Total parking spaces")
    
    # Amenities
    amenities: List[Amenity] = Field(default_factory=list, description="Property amenities")
    
    # Market Information
    listed_date: datetime = Field(..., description="Date property was listed")
    days_on_market: int = Field(..., ge=0, description="Number of days on market")
    listing_agent: str = Field(..., description="Name of listing agent")
    listing_agency: Optional[str] = Field(None, description="Listing agency/brokerage")
    
    # Calculated Proximity (populated by geocoding service)
    distance_to_metro: Optional[float] = Field(None, ge=0, description="Distance to nearest metro station (km)")
    distance_to_schools: Optional[float] = Field(None, ge=0, description="Distance to nearest school (km)")
    distance_to_shopping: Optional[float] = Field(None, ge=0, description="Distance to shopping areas (km)")
    walkability_score: Optional[int] = Field(None, ge=0, le=100, description="Walkability score (0-100)")
    
    # Additional Data
    hoa_fees: Optional[int] = Field(None, ge=0, description="Monthly HOA fees")
    property_taxes: Optional[int] = Field(None, ge=0, description="Annual property taxes")
    
    # Flexible additional fields
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")
    
    @validator('state')
    def validate_state(cls, v):
        """Ensure state is uppercase."""
        return v.upper() if v else v
    
    @validator('zip_code')
    def validate_zip_code(cls, v):
        """Basic ZIP code validation."""
        if v and not (v.isdigit() and len(v) == 5):
            # Allow ZIP+4 format
            if not (len(v) == 10 and v[:5].isdigit() and v[5] == '-' and v[6:].isdigit()):
                raise ValueError('ZIP code must be 5 digits or ZIP+4 format')
        return v
    
    @property
    def price_per_sqft(self) -> float:
        """Calculate price per square foot."""
        return self.price / self.square_feet if self.square_feet > 0 else 0
    
    @property
    def is_new_construction(self) -> bool:
        """Check if property is new construction (built within last 2 years)."""
        if not self.year_built:
            return False
        current_year = datetime.now().year
        return current_year - self.year_built <= 2


class PropertyListing(BaseModel):
    """Complete property listing with description and metadata."""
    
    # Core content for semantic search
    title: str = Field(..., description="Property listing title")
    description: str = Field(..., description="Detailed property description")
    
    # Structured metadata for filtering
    metadata: PropertyMetadata = Field(..., description="Property metadata for filtering")
    
    # Additional content
    photos: List[str] = Field(default_factory=list, description="List of photo URLs")
    virtual_tour_url: Optional[str] = Field(None, description="Virtual tour URL")
    floor_plan_url: Optional[str] = Field(None, description="Floor plan URL")
    
    # System fields
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def get_searchable_content(self) -> str:
        """Get content for embedding and semantic search."""
        content_parts = [
            self.title,
            self.description,
            f"{self.metadata.property_type.value} in {self.metadata.neighborhood}, {self.metadata.city}",
            f"{self.metadata.bedrooms} bedrooms, {self.metadata.bathrooms} bathrooms",
            f"{self.metadata.square_feet} square feet",
        ]
        
        if self.metadata.amenities:
            amenities_str = ", ".join([amenity.value.replace('_', ' ') for amenity in self.metadata.amenities])
            content_parts.append(f"Amenities: {amenities_str}")
        
        if self.metadata.year_built:
            content_parts.append(f"Built in {self.metadata.year_built}")
            
        return " | ".join(content_parts)
    
    def to_dict_for_pinecone(self) -> dict:
        """Convert to dictionary format suitable for Pinecone."""
        return {
            "id": self.metadata.property_id,
            "values": [],  # Will be populated with embeddings
            "metadata": {
                # Core searchable fields
                "title": self.title,
                "description": self.description,
                "searchable_content": self.get_searchable_content(),
                
                # Filterable metadata
                "property_type": self.metadata.property_type.value,
                "status": self.metadata.status.value,
                "price": self.metadata.price,
                "bedrooms": self.metadata.bedrooms,
                "bathrooms": self.metadata.bathrooms,
                "square_feet": self.metadata.square_feet,
                "city": self.metadata.city,
                "state": self.metadata.state,
                "zip_code": self.metadata.zip_code,
                "neighborhood": self.metadata.neighborhood,
                "year_built": self.metadata.year_built,
                "days_on_market": self.metadata.days_on_market,
                "amenities": [amenity.value for amenity in self.metadata.amenities],
                
                # Coordinates for geo-filtering
                "latitude": self.metadata.latitude,
                "longitude": self.metadata.longitude,
                
                # Proximity data
                "distance_to_metro": self.metadata.distance_to_metro,
                "walkability_score": self.metadata.walkability_score,
                
                # Calculated fields
                "price_per_sqft": self.metadata.price_per_sqft,
                "is_new_construction": self.metadata.is_new_construction,
                
                # System fields
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            }
        }


class SearchQuery(BaseModel):
    """User search query with filters and preferences."""
    
    # Raw user query
    query: str = Field(..., description="Natural language search query")
    
    # Extracted filters (will be populated by query analyzer)
    filters: Dict[str, Any] = Field(default_factory=dict, description="Extracted metadata filters")
    
    # Search preferences
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of results")
    location_preference: Optional[str] = Field(None, description="Preferred location/neighborhood")
    
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