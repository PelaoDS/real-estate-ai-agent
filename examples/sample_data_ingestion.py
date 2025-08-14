"""Sample data ingestion script for the Real Estate AI Agent."""

import json
from datetime import datetime, timedelta
from typing import List
import random

from src.real_estate_agent.schemas import PropertyListing, PropertyMetadata, PropertyType, Amenity, PropertyStatus
from src.real_estate_agent.pinecone_client import pinecone_client


def create_sample_properties() -> List[PropertyListing]:
    """Create sample property data for testing."""
    
    properties = []
    
    # Sample property data
    sample_data = [
        {
            "title": "Luxury Waterfront Condo in Miami Beach",
            "description": "Stunning 2-bedroom, 2-bathroom condo with breathtaking ocean views. Features modern kitchen with granite countertops, spacious living area, and private balcony overlooking the water. Building amenities include pool, gym, and 24-hour concierge.",
            "property_type": PropertyType.CONDO,
            "price": 750000,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "square_feet": 1200,
            "city": "Miami Beach",
            "state": "FL",
            "neighborhood": "South Beach",
            "year_built": 2020,
            "amenities": [Amenity.POOL, Amenity.GYM, Amenity.BALCONY, Amenity.PARKING],
            "listing_agent": "Maria Rodriguez"
        },
        {
            "title": "Modern Family House in Austin",
            "description": "Beautiful 4-bedroom, 3-bathroom house perfect for families. Open floor plan with updated kitchen, hardwood floors throughout, and large backyard. Great neighborhood with excellent schools nearby.",
            "property_type": PropertyType.HOUSE,
            "price": 485000,
            "bedrooms": 4,
            "bathrooms": 3.0,
            "square_feet": 2200,
            "city": "Austin",
            "state": "TX",
            "neighborhood": "Cedar Park",
            "year_built": 2018,
            "amenities": [Amenity.HARDWOOD_FLOORS, Amenity.FIREPLACE, Amenity.PARKING],
            "listing_agent": "John Smith"
        },
        {
            "title": "Cozy Studio in Manhattan",
            "description": "Charming studio apartment in the heart of Manhattan. Recently renovated with modern appliances, high ceilings, and large windows providing plenty of natural light. Walking distance to subway and restaurants.",
            "property_type": PropertyType.STUDIO,
            "price": 320000,
            "bedrooms": 0,
            "bathrooms": 1.0,
            "square_feet": 450,
            "city": "New York",
            "state": "NY",
            "neighborhood": "Chelsea",
            "year_built": 1995,
            "amenities": [Amenity.DISHWASHER, Amenity.HARDWOOD_FLOORS],
            "listing_agent": "Sarah Johnson"
        },
        {
            "title": "Luxury Townhouse in San Francisco",
            "description": "Elegant 3-bedroom, 2.5-bathroom townhouse with panoramic city views. Features gourmet kitchen, fireplace, private garage, and rooftop deck. Located in prestigious neighborhood with easy access to tech companies.",
            "property_type": PropertyType.TOWNHOUSE,
            "price": 1200000,
            "bedrooms": 3,
            "bathrooms": 2.5,
            "square_feet": 1800,
            "city": "San Francisco",
            "state": "CA",
            "neighborhood": "Nob Hill",
            "year_built": 2019,
            "amenities": [Amenity.FIREPLACE, Amenity.PARKING, Amenity.HARDWOOD_FLOORS, Amenity.DISHWASHER],
            "listing_agent": "David Chen"
        },
        {
            "title": "Pet-Friendly Apartment in Denver",
            "description": "Spacious 2-bedroom, 1-bathroom apartment perfect for pet owners. Features in-unit washer/dryer, air conditioning, and private balcony. Pet-friendly building with dog park nearby. Close to hiking trails.",
            "property_type": PropertyType.APARTMENT,
            "price": 275000,
            "bedrooms": 2,
            "bathrooms": 1.0,
            "square_feet": 950,
            "city": "Denver",
            "state": "CO",
            "neighborhood": "Capitol Hill",
            "year_built": 2015,
            "amenities": [Amenity.PET_FRIENDLY, Amenity.WASHER_DRYER, Amenity.AIR_CONDITIONING, Amenity.BALCONY],
            "listing_agent": "Lisa Martinez"
        },
        {
            "title": "Beachfront House in San Diego",
            "description": "Amazing 5-bedroom, 4-bathroom house right on the beach. Features ocean views from every room, chef's kitchen, master suite with walk-in closet, and private pool. Perfect for entertaining and beach lifestyle.",
            "property_type": PropertyType.HOUSE,
            "price": 2500000,
            "bedrooms": 5,
            "bathrooms": 4.0,
            "square_feet": 3200,
            "city": "San Diego",
            "state": "CA",
            "neighborhood": "La Jolla",
            "year_built": 2021,
            "amenities": [Amenity.POOL, Amenity.WALK_IN_CLOSET, Amenity.DISHWASHER, Amenity.PARKING],
            "listing_agent": "Michael Brown"
        },
        {
            "title": "High-Rise Condo in Chicago",
            "description": "Stunning 3-bedroom, 2-bathroom condo on the 25th floor with city skyline views. Modern amenities include granite countertops, stainless steel appliances, and floor-to-ceiling windows. Building has gym and rooftop deck.",
            "property_type": PropertyType.CONDO,
            "price": 625000,
            "bedrooms": 3,
            "bathrooms": 2.0,
            "square_feet": 1500,
            "city": "Chicago",
            "state": "IL",
            "neighborhood": "River North",
            "year_built": 2017,
            "amenities": [Amenity.GYM, Amenity.DISHWASHER, Amenity.PARKING, Amenity.ROOF_DECK],
            "listing_agent": "Jennifer Wilson"
        },
        {
            "title": "Charming Cottage in Portland",
            "description": "Adorable 2-bedroom, 1-bathroom cottage with vintage charm and modern updates. Features original hardwood floors, cozy fireplace, and beautiful garden. Perfect for first-time buyers in trendy neighborhood.",
            "property_type": PropertyType.HOUSE,
            "price": 395000,
            "bedrooms": 2,
            "bathrooms": 1.0,
            "square_feet": 1100,
            "city": "Portland",
            "state": "OR",
            "neighborhood": "Alberta",
            "year_built": 1955,
            "amenities": [Amenity.HARDWOOD_FLOORS, Amenity.FIREPLACE],
            "listing_agent": "Ryan Thompson"
        }
    ]
    
    # Create PropertyListing objects
    for i, data in enumerate(sample_data):
        property_id = f"PROP_{i+1:03d}"
        
        metadata = PropertyMetadata(
            property_id=property_id,
            property_type=data["property_type"],
            status=PropertyStatus.ACTIVE,
            price=data["price"],
            bedrooms=data["bedrooms"],
            bathrooms=data["bathrooms"],
            square_feet=data["square_feet"],
            city=data["city"],
            state=data["state"],
            neighborhood=data["neighborhood"],
            year_built=data["year_built"],
            amenities=data["amenities"],
            days_on_market=random.randint(1, 60),
            listing_agent=data["listing_agent"]
        )
        
        property_listing = PropertyListing(
            title=data["title"],
            description=data["description"],
            metadata=metadata
        )
        
        properties.append(property_listing)
    
    return properties


def ingest_sample_data():
    """Ingest sample property data into Pinecone."""
    
    print("🏠 Creating sample property data...")
    properties = create_sample_properties()
    
    print(f"📝 Generated {len(properties)} sample properties")
    
    # Upsert to Pinecone
    print("📤 Uploading to Pinecone...")
    result = pinecone_client.upsert_properties(properties)
    
    print("✅ Data ingestion completed!")
    print(f"   - Total properties: {result['total']}")
    print(f"   - Successfully uploaded: {result['successful']}")
    print(f"   - Failed: {result['failed']}")
    
    # Get stats
    print("\\n📊 Database statistics:")
    stats = pinecone_client.get_index_stats()
    print(f"   - Total vectors in index: {stats.get('total_vectors', 0)}")
    

def save_sample_data_json():
    """Save sample data to JSON file for reference."""
    properties = create_sample_properties()
    
    # Convert to serializable format
    json_data = []
    for prop in properties:
        json_data.append({
            "property_id": prop.metadata.property_id,
            "title": prop.title,
            "description": prop.description,
            "price": prop.metadata.price,
            "bedrooms": prop.metadata.bedrooms,
            "bathrooms": prop.metadata.bathrooms,
            "square_feet": prop.metadata.square_feet,
            "property_type": prop.metadata.property_type.value,
            "city": prop.metadata.city,
            "state": prop.metadata.state,
            "neighborhood": prop.metadata.neighborhood,
            "amenities": [a.value for a in prop.metadata.amenities],
            "listing_agent": prop.metadata.listing_agent,
            "year_built": prop.metadata.year_built
        })
    
    with open("data/sample_properties.json", "w") as f:
        json.dump(json_data, f, indent=2)
    
    print("💾 Sample data saved to data/sample_properties.json")


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    import os
    os.makedirs("data", exist_ok=True)
    
    # Save sample data to JSON
    save_sample_data_json()
    
    # Ingest to Pinecone
    ingest_sample_data()