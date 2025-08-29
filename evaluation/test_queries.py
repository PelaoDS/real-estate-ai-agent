"""Ground truth test queries for evaluation."""

from typing import List, Dict, Any

# Test queries with expected property matches
TEST_QUERIES = [
    {
        "query": "I want a luxury condo in Miami with ocean views and pool",
        "expected_properties": ["PROP_001"],  # Miami Beach waterfront condo
        "description": "Should find the Miami Beach waterfront condo with pool and ocean views"
    },
    {
        "query": "Family house with 4 bedrooms under 500k",
        "expected_properties": ["PROP_002", "PROP_010"],  # Austin house and Phoenix house
        "description": "Should find family homes with 4+ bedrooms under $500k"
    },
    {
        "query": "Studio apartment in Manhattan for under 350k",
        "expected_properties": ["PROP_003"],  # Chelsea studio
        "description": "Should find the Manhattan studio in Chelsea"
    },
    {
        "query": "Townhouse in San Francisco with fireplace",
        "expected_properties": ["PROP_004"],  # SF townhouse in Nob Hill
        "description": "Should find the luxury townhouse in Nob Hill with fireplace"
    },
    {
        "query": "Pet friendly apartment in Denver with balcony",
        "expected_properties": ["PROP_005"],  # Denver pet-friendly apartment
        "description": "Should find the Capitol Hill apartment that allows pets"
    },
    {
        "query": "Beachfront house in California over 2 million",
        "expected_properties": ["PROP_006"],  # San Diego beachfront house
        "description": "Should find the expensive beachfront property in La Jolla"
    },
    {
        "query": "High rise condo in Chicago with gym access",
        "expected_properties": ["PROP_007"],  # Chicago high-rise
        "description": "Should find the River North condo with gym amenities"
    },
    {
        "query": "Historic house in Portland with original hardwood floors",
        "expected_properties": ["PROP_008"],  # Portland cottage
        "description": "Should find the vintage cottage in Alberta neighborhood"
    },
    {
        "query": "Modern loft in Brooklyn with exposed brick",
        "expected_properties": ["PROP_009"],  # Brooklyn loft
        "description": "Should find the industrial loft in Williamsburg"
    },
    {
        "query": "Properties with pools in warm climates",
        "expected_properties": ["PROP_001", "PROP_006", "PROP_010"],  # Miami, San Diego, Phoenix
        "description": "Should find multiple properties with pools in FL, CA, and AZ"
    }
]


def get_test_queries() -> List[Dict[str, Any]]:
    """Return the list of test queries for evaluation."""
    return TEST_QUERIES


def get_query_by_index(index: int) -> Dict[str, Any]:
    """Get a specific test query by index."""
    if 0 <= index < len(TEST_QUERIES):
        return TEST_QUERIES[index]
    else:
        raise IndexError(f"Query index {index} out of range (0-{len(TEST_QUERIES)-1})")