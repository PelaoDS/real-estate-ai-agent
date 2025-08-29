"""Sample data ingestion script with expanded dataset for Real Estate AI Agent."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timedelta
from typing import List
import random

from src.real_estate_agent.schemas import PropertyListing, PropertyMetadata, PropertyType, Amenity, PropertyStatus
from src.real_estate_agent.pinecone_client import pinecone_client


def create_sample_properties() -> List[PropertyListing]:
    """Create expanded sample property data for testing (12 properties)."""
    
    properties = []
    
    # Expanded sample data with comprehensive descriptions
    sample_data = [
        {
            "title": "Luxury Waterfront Condo in Miami Beach",
            "description": "Stunning 2-bedroom, 2-bathroom oceanfront condominium with breathtaking panoramic water views from floor-to-ceiling windows. This modern unit features an open-concept living design with premium granite countertops, stainless steel appliances, and custom cabinetry. The spacious master suite includes a walk-in closet and spa-like en-suite bathroom with marble finishes. Private balcony perfect for morning coffee overlooking the Atlantic Ocean. Building amenities include resort-style pool deck, state-of-the-art fitness center, 24-hour concierge, and valet parking. Located in prestigious South Beach with easy access to world-class dining, shopping, and entertainment.",
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
            "description": "Beautiful single-family home featuring 4 spacious bedrooms and 3 full bathrooms, perfect for growing families. This contemporary design showcases an open floor plan with soaring ceilings and abundant natural light throughout. The gourmet kitchen boasts quartz countertops, professional-grade stainless steel appliances, and large center island ideal for entertaining. Genuine hardwood flooring flows seamlessly from room to room. The master suite offers a luxurious retreat with walk-in closet and dual vanity bathroom. Private backyard with mature landscaping provides space for outdoor activities and gardening. Located in highly-rated school district with parks and family amenities nearby.",
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
            "description": "Charming studio apartment strategically located in the vibrant heart of Manhattan's Chelsea neighborhood. This recently renovated unit maximizes every square foot with intelligent design and premium finishes. Features include modern stainless steel appliances, sleek granite countertops, and custom built-in storage solutions. High ceilings and oversized windows create an airy feel while flooding the space with natural light. Original hardwood floors add warmth and character. The updated bathroom includes contemporary fixtures and efficient layout. Building provides excellent maintenance and security. Prime location offers unbeatable walkability with subway stations, acclaimed restaurants, shopping, and cultural attractions all within blocks.",
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
            "description": "Elegant three-bedroom, two-and-half-bathroom townhouse offering spectacular panoramic views of San Francisco's iconic skyline and bay. This sophisticated residence features a gourmet kitchen equipped with top-of-the-line appliances, custom cabinetry, and premium stone countertops. The living area centers around a beautiful fireplace creating perfect ambiance for relaxation. Original architectural details blend seamlessly with modern updates throughout. Private two-car garage provides secure parking in this premium location. The master bedroom includes walk-in closet and luxury bathroom with dual vanities. Located in the prestigious Nob Hill neighborhood with convenient access to major technology companies, fine dining, and cultural attractions.",
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
            "description": "Spacious two-bedroom, one-bathroom apartment designed with pet owners in mind. This well-appointed unit features in-unit washer and dryer for convenience, central air conditioning for year-round comfort, and private balcony overlooking tree-lined streets. The modern kitchen includes energy-efficient appliances and ample cabinet storage. Both bedrooms offer generous closet space and large windows. The pet-friendly building welcomes furry companions with nearby dog park and walking trails. Located in trendy Capitol Hill neighborhood known for its vibrant arts scene, local breweries, and easy access to outdoor recreation including hiking and biking trails in the nearby foothills.",
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
            "description": "Extraordinary five-bedroom, four-bathroom oceanfront estate offering unparalleled luxury and direct beach access. Every room showcases stunning Pacific Ocean views through expansive windows and sliding glass doors. The chef's kitchen features professional-grade appliances, granite countertops, and custom cabinetry perfect for entertaining. The master suite serves as a private retreat with panoramic ocean views, walk-in closet, and spa-like bathroom with soaking tub. Private swimming pool and outdoor living areas create an resort-like atmosphere. Additional bedrooms offer flexibility for guests or home office space. The property includes direct beach access, making it ideal for the California coastal lifestyle with surfing, swimming, and beachside relaxation.",
            "property_type": PropertyType.HOUSE,
            "price": 2500000,
            "bedrooms": 5,
            "bathrooms": 4.0,
            "square_feet": 3200,
            "city": "San Diego",
            "state": "CA",
            "neighborhood": "La Jolla",
            "year_built": 2021,
            "amenities": [Amenity.POOL, Amenity.HARDWOOD_FLOORS, Amenity.DISHWASHER, Amenity.PARKING],
            "listing_agent": "Michael Brown"
        },
        {
            "title": "High-Rise Condo in Chicago",
            "description": "Stunning three-bedroom, two-bathroom condominium on the 25th floor offering breathtaking city skyline views. This modern unit features floor-to-ceiling windows maximizing natural light and showcasing Chicago's architectural beauty. The kitchen includes premium granite countertops, stainless steel appliances, and contemporary cabinetry. Open living and dining areas provide ideal space for entertaining with spectacular urban backdrop. The master bedroom offers city views and generous closet space. Building amenities include professionally equipped fitness center, rooftop deck with panoramic views, and secure parking garage. Located in trendy River North neighborhood with easy access to downtown business district, world-class restaurants, shopping along Magnificent Mile, and lakefront recreational activities.",
            "property_type": PropertyType.CONDO,
            "price": 625000,
            "bedrooms": 3,
            "bathrooms": 2.0,
            "square_feet": 1500,
            "city": "Chicago",
            "state": "IL",
            "neighborhood": "River North",
            "year_built": 2017,
            "amenities": [Amenity.GYM, Amenity.DISHWASHER, Amenity.PARKING],
            "listing_agent": "Jennifer Wilson"
        },
        {
            "title": "Charming Cottage in Portland",
            "description": "Adorable two-bedroom, one-bathroom cottage combining vintage charm with thoughtful modern updates. This character-filled home features original hardwood floors throughout, adding warmth and historic appeal. The living room centers around a cozy brick fireplace perfect for Portland's cooler evenings. Updated kitchen maintains period charm while offering modern functionality. Both bedrooms provide comfortable spaces with good natural light and original architectural details. The property includes a beautifully maintained garden with mature plantings and space for outdoor relaxation. Located in the trendy Alberta neighborhood known for its artistic community, local cafes, and easy access to public transportation. Perfect for first-time buyers seeking character and convenient urban location.",
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
        },
        # NEW PROPERTIES (4 additional)
        {
            "title": "Modern Loft in Brooklyn",
            "description": "Industrial-chic two-bedroom, two-bathroom loft featuring soaring 12-foot ceilings, exposed brick walls, and polished concrete floors. This converted warehouse space offers an open floor plan ideal for contemporary living and entertaining. The kitchen showcases stainless steel appliances, quartz countertops, and custom steel cabinetry maintaining the industrial aesthetic. Large windows provide abundant natural light and views of the Manhattan skyline. The master bedroom includes an en-suite bathroom and walk-in closet. Additional bedroom works perfectly as guest room or home office. Building amenities include fitness center, rooftop terrace with city views, and bike storage. Located in trendy Williamsburg with easy subway access to Manhattan, surrounded by artisanal coffee shops, galleries, and Brooklyn's famous food scene.",
            "property_type": PropertyType.CONDO,
            "price": 895000,
            "bedrooms": 2,
            "bathrooms": 2.0,
            "square_feet": 1350,
            "city": "Brooklyn",
            "state": "NY",
            "neighborhood": "Williamsburg",
            "year_built": 2016,
            "amenities": [Amenity.GYM, Amenity.DISHWASHER, Amenity.HARDWOOD_FLOORS],
            "listing_agent": "Alex Rivera"
        },
        {
            "title": "Family Home with Pool in Phoenix",
            "description": "Spacious four-bedroom, three-bathroom single-family home with resort-style backyard oasis. This well-maintained property features tile flooring throughout for easy maintenance in the desert climate, updated kitchen with granite countertops and energy-efficient appliances. The open floor plan connects kitchen, dining, and living areas perfect for family gatherings. Central air conditioning ensures comfort during Arizona's warm months. The master suite includes walk-in closet and private bathroom with dual sinks. Three additional bedrooms provide flexibility for children, guests, or home office space. The highlight is the backyard featuring sparkling swimming pool, covered patio for outdoor dining, and low-maintenance desert landscaping. Two-car garage provides covered parking and storage.",
            "property_type": PropertyType.HOUSE,
            "price": 425000,
            "bedrooms": 4,
            "bathrooms": 3.0,
            "square_feet": 2400,
            "city": "Phoenix",
            "state": "AZ",
            "neighborhood": "Ahwatukee",
            "year_built": 2010,
            "amenities": [Amenity.POOL, Amenity.AIR_CONDITIONING, Amenity.PARKING],
            "listing_agent": "Carlos Mendoza"
        },
        {
            "title": "Historic Brownstone in Boston",
            "description": "Magnificent three-bedroom, two-bathroom brownstone showcasing classic Boston architecture with modern conveniences. This meticulously maintained property features original hardwood floors, high ceilings with decorative moldings, and working fireplace with original mantle. The updated kitchen preserves period charm while incorporating contemporary appliances and functionality. Spacious living and dining rooms maintain historic character with bay windows and original architectural details. The master bedroom offers generous space and period fixtures. Two additional bedrooms provide comfortable accommodations with good natural light. Private basement level includes laundry facilities with washer and dryer. Located on a tree-lined street in prestigious Back Bay neighborhood within walking distance of public transportation, Boston Common, and the city's finest cultural attractions.",
            "property_type": PropertyType.TOWNHOUSE,
            "price": 1150000,
            "bedrooms": 3,
            "bathrooms": 2.0,
            "square_feet": 1900,
            "city": "Boston",
            "state": "MA",
            "neighborhood": "Back Bay",
            "year_built": 1890,
            "amenities": [Amenity.FIREPLACE, Amenity.HARDWOOD_FLOORS, Amenity.WASHER_DRYER],
            "listing_agent": "Patricia O'Brien"
        },
        {
            "title": "Modern Apartment with City Views in Seattle",
            "description": "Contemporary one-bedroom, one-bathroom apartment on the 15th floor with spectacular views of Seattle's skyline and Mount Rainier. This sleek unit features floor-to-ceiling windows, modern kitchen with quartz countertops and stainless steel appliances, and in-unit washer and dryer for convenience. The open living area maximizes space and light with clean lines and neutral finishes. The bedroom comfortably accommodates a king bed with built-in closet storage. Modern bathroom includes walk-in shower with glass enclosure. Building amenities feature rooftop terrace, fitness center, and secure parking. Pet-friendly policy welcomes furry companions. Located in trendy Capitol Hill with easy access to public transportation, Pike Place Market, and Seattle's thriving tech corridor. Walking distance to coffee shops, restaurants, and cultural venues.",
            "property_type": PropertyType.APARTMENT,
            "price": 385000,
            "bedrooms": 1,
            "bathrooms": 1.0,
            "square_feet": 750,
            "city": "Seattle",
            "state": "WA",
            "neighborhood": "Capitol Hill",
            "year_built": 2019,
            "amenities": [Amenity.PET_FRIENDLY, Amenity.WASHER_DRYER, Amenity.GYM, Amenity.PARKING],
            "listing_agent": "Jessica Wong"
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
    
    print("Creating expanded property dataset...")
    properties = create_sample_properties()
    
    print(f"Generated {len(properties)} sample properties with detailed descriptions")
    
    # Clear existing data first
    print("Clearing existing data from Pinecone...")
    try:
        pinecone_client.index.delete(delete_all=True)
        print("Successfully cleared existing data")
    except Exception as e:
        print(f"Note: {e}")
    
    # Upsert to Pinecone
    print("Uploading to Pinecone with description vectorization...")
    result = pinecone_client.upsert_properties(properties)
    
    print("Data ingestion completed!")
    print(f"   - Total properties: {result['total']}")
    print(f"   - Successfully uploaded: {result['successful']}")
    print(f"   - Failed: {result['failed']}")
    
    # Get stats
    print("\nDatabase statistics:")
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
    
    print("Sample data saved to data/sample_properties.json")


if __name__ == "__main__":
    # Create data directory if it doesn't exist
    import os
    os.makedirs("data", exist_ok=True)
    
    # Save sample data to JSON
    save_sample_data_json()
    
    # Ingest to Pinecone
    ingest_sample_data()