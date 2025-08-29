"""Basic usage example for the Real Estate AI Agent."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.real_estate_agent.agent import real_estate_agent


def main():
    """Demonstrate basic usage of the real estate agent."""
    
    print("🏠 Real Estate AI Agent (GPT-5) - Basic Usage Example")
    print("=" * 60)
    
    # Test queries
    test_queries = [
        "Dame una propiedad que esté en un piso 24 o más",
        "I'm looking for a 2 bedroom apartment in Miami under $400,000",
        "Show me luxury condos in New York with amenities like pool and gym",
        "Find me a house in California with at least 3 bedrooms and a garage",
        "What properties do you have with a fireplace and hardwood floors?",
        "I need a studio apartment that allows pets"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 50)
        
        try:
            response = real_estate_agent.search_properties(query)
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "="*60)
    
    # Database stats
    print("\n📊 Database Information:")
    print("-" * 30)
    try:
        db_info = real_estate_agent.get_database_info()
        print(db_info)
    except Exception as e:
        print(f"❌ Error getting database info: {e}")


if __name__ == "__main__":
    main()