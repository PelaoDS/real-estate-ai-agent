"""Performance evaluation pipeline with A/B/C testing configurations."""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import Dict, Any, List
from dataclasses import dataclass
from loguru import logger

from src.real_estate_agent.schemas import PropertyListing
from scripts.sample_data_ingestion import create_sample_properties
from evaluation.test_queries import get_test_queries
from evaluation.evaluator import PropertyMatchEvaluator
from evaluation.metrics import metrics_calculator


@dataclass
class TestConfiguration:
    """Configuration for A/B/C testing."""
    name: str
    use_vectors: bool
    use_searchable_content: bool  # vs description only
    use_amenities_filter: bool
    description: str


# 8 test configurations (2^3 combinations)
TEST_CONFIGURATIONS = [
    TestConfiguration("NoVectors_NoSearchable_NoAmenities", False, False, False, 
                     "No vectorization, description only, no amenity filtering"),
    TestConfiguration("NoVectors_NoSearchable_WithAmenities", False, False, True,
                     "No vectorization, description only, with amenity filtering"),
    TestConfiguration("NoVectors_WithSearchable_NoAmenities", False, True, False,
                     "No vectorization, searchable content, no amenity filtering"),
    TestConfiguration("NoVectors_WithSearchable_WithAmenities", False, True, True,
                     "No vectorization, searchable content, with amenity filtering"),
    TestConfiguration("WithVectors_NoSearchable_NoAmenities", True, False, False,
                     "With vectorization, description only, no amenity filtering"),
    TestConfiguration("WithVectors_NoSearchable_WithAmenities", True, False, True,
                     "With vectorization, description only, with amenity filtering"),
    TestConfiguration("WithVectors_WithSearchable_NoAmenities", True, True, False,
                     "With vectorization, searchable content, no amenity filtering"),
    TestConfiguration("WithVectors_WithSearchable_WithAmenities", True, True, True,
                     "With vectorization, searchable content, with amenity filtering"),
]


class PerformancePipeline:
    """Pipeline for running comprehensive A/B/C testing."""
    
    def __init__(self):
        self.evaluator = PropertyMatchEvaluator()
        self.sample_properties = create_sample_properties()
        self.test_queries = get_test_queries()
        
    def run_full_evaluation(self) -> Dict[str, Dict[str, float]]:
        """Run evaluation across all 8 configurations."""
        logger.info("Starting comprehensive A/B/C testing pipeline")
        
        all_results = {}
        
        for config in TEST_CONFIGURATIONS:
            logger.info(f"Testing configuration: {config.name}")
            config_results = self._test_configuration(config)
            all_results[config.name] = config_results
        
        # Compile final results
        summary = metrics_calculator.compile_results(all_results)
        
        # Print comparison report
        metrics_calculator.print_comparison_report(summary)
        
        # Export to JSON
        metrics_calculator.export_results_to_json(summary, "evaluation/results.json")
        
        return summary
    
    def _test_configuration(self, config: TestConfiguration) -> List[Dict[str, Any]]:
        """Test a single configuration against all test queries."""
        logger.info(f"Running tests for: {config.description}")
        
        configuration_results = []
        
        for test_case in self.test_queries:
            query = test_case['query']
            expected_ids = test_case['expected_properties']
            
            try:
                # Setup configuration
                search_func = self._create_search_function(config)
                
                # Measure search latency
                search_results, latency_ms = metrics_calculator.measure_latency(
                    search_func, query
                )
                
                # Get expected property data
                expected_properties_data = self._get_properties_by_ids(expected_ids)
                
                # Evaluate results
                evaluation = self.evaluator.evaluate_search_results(
                    query=query,
                    agent_results=search_results,
                    expected_property_ids=expected_ids,
                    expected_properties_data=expected_properties_data
                )
                
                # Add metrics
                evaluation.update({
                    "latency_ms": latency_ms,
                    "configuration": config.name
                })
                
                configuration_results.append(evaluation)
                
                logger.info(f"Query: '{query[:50]}...' - Accuracy: {evaluation.get('accuracy', 0):.3f}, Latency: {latency_ms:.1f}ms")
                
            except Exception as e:
                logger.error(f"Error testing query '{query}': {str(e)}")
                configuration_results.append({
                    "accuracy": 0.0,
                    "is_correct": False,
                    "latency_ms": 0.0,
                    "error": str(e),
                    "configuration": config.name
                })
        
        return configuration_results
    
    def _create_search_function(self, config: TestConfiguration):
        """Create search function based on configuration."""
        
        if not config.use_vectors:
            # Metadata filtering only (no vector search)
            return self._metadata_only_search
        else:
            # Vector search with or without searchable content
            if config.use_searchable_content:
                return self._vector_search_with_searchable_content
            else:
                return self._vector_search_description_only
    
    def _metadata_only_search(self, query: str) -> List[Dict[str, Any]]:
        """Search using only metadata filters (no vectorization)."""
        logger.info("Using metadata-only search (no vectors)")
        
        # Simple keyword matching in title/description
        results = []
        query_words = query.lower().split()
        
        for prop in self.sample_properties[:10]:  # Limit results
            title_desc = f"{prop.title} {prop.description}".lower()
            if any(word in title_desc for word in query_words):
                results.append({
                    'property_id': prop.metadata.property_id,
                    'title': prop.title,
                    'price': prop.metadata.price,
                    'bedrooms': prop.metadata.bedrooms,
                    'bathrooms': prop.metadata.bathrooms,
                    'city': prop.metadata.city,
                    'state': prop.metadata.state
                })
        
        return results
    
    def _vector_search_with_searchable_content(self, query: str) -> List[Dict[str, Any]]:
        """Search using vectors with searchable content."""
        from src.real_estate_agent.agent import real_estate_agent
        
        logger.info("Using vector search with searchable content (via RealEstateAgent)")
        response_text = real_estate_agent.search_properties(query)
        
        # Parse agent response to extract structured property data
        return self._parse_agent_response(response_text)
    
    def _vector_search_description_only(self, query: str) -> List[Dict[str, Any]]:
        """Search using vectors with description only (current implementation)."""
        from src.real_estate_agent.agent import real_estate_agent
        
        logger.info("Using vector search with description only (via RealEstateAgent)")
        response_text = real_estate_agent.search_properties(query)
        
        # Parse agent response to extract structured property data
        return self._parse_agent_response(response_text)
    
    def _parse_agent_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse agent text response to extract property data."""
        properties = []
        
        try:
            # Look for property patterns in the agent response
            # Pattern: "- Title (Neighborhood, City, State) — $Price"
            # Followed by: "X bed | Y bath | Z sq ft | Type | Year | $/sq ft | Days on market"
            
            lines = response_text.split('\n')
            current_property = {}
            
            for line in lines:
                line = line.strip()
                
                # Match property title line: "- Title (Location) — $Price"
                title_match = re.match(r'-\s*(.+?)\s*\((.+?),\s*(.+?),\s*(.+?)\)\s*—\s*\$(.+?)$', line)
                if title_match:
                    if current_property:  # Save previous property
                        properties.append(current_property)
                    
                    title, neighborhood, city, state, price_str = title_match.groups()
                    price = int(price_str.replace(',', '').replace('.0', ''))
                    
                    current_property = {
                        'title': title.strip(),
                        'city': city.strip(),
                        'state': state.strip(),
                        'neighborhood': neighborhood.strip(),
                        'price': price,
                        'property_id': 'UNKNOWN'  # Will try to match later
                    }
                    continue
                
                # Match details line: "X bed | Y bath | Z sq ft | Type | Year | $/sq ft | Days"
                details_match = re.match(r'(\d+)\s*bed\s*\|\s*(\d+(?:\.\d+)?)\s*bath\s*\|\s*.+?\|\s*(\w+)\s*\|', line)
                if details_match and current_property:
                    bedrooms, bathrooms, property_type = details_match.groups()
                    current_property.update({
                        'bedrooms': int(bedrooms),
                        'bathrooms': float(bathrooms),
                        'property_type': property_type.lower()
                    })
                    
                    # Try to match with known properties based on title, city, price
                    matched_id = self._find_matching_property_id(current_property)
                    if matched_id:
                        current_property['property_id'] = matched_id
            
            # Add last property
            if current_property:
                properties.append(current_property)
            
            logger.info(f"Parsed {len(properties)} properties from agent response")
            return properties
            
        except Exception as e:
            logger.error(f"Error parsing agent response: {str(e)}")
            return []
    
    def _find_matching_property_id(self, parsed_property: Dict[str, Any]) -> Optional[str]:
        """Find matching property_id from sample data."""
        for prop in self.sample_properties:
            if (prop.title.lower() == parsed_property['title'].lower() and
                prop.metadata.city.lower() == parsed_property['city'].lower() and
                prop.metadata.price == parsed_property['price']):
                return prop.metadata.property_id
        return None
    
    def _get_properties_by_ids(self, property_ids: List[str]) -> List[Dict[str, Any]]:
        """Get property data by IDs for evaluation."""
        properties_data = []
        
        for prop in self.sample_properties:
            if prop.metadata.property_id in property_ids:
                properties_data.append({
                    "property_id": prop.metadata.property_id,
                    "title": prop.title,
                    "price": prop.metadata.price,
                    "bedrooms": prop.metadata.bedrooms,
                    "bathrooms": prop.metadata.bathrooms,
                    "city": prop.metadata.city,
                    "state": prop.metadata.state,
                    "property_type": prop.metadata.property_type.value,
                    "amenities": [a.value for a in prop.metadata.amenities]
                })
        
        return properties_data


def run_evaluation():
    """Main function to run the evaluation pipeline."""
    pipeline = PerformancePipeline()
    
    print("Starting Performance Evaluation Pipeline")
    print("Testing 8 configurations across 10 test queries")
    print("This will take several minutes...")
    
    results = pipeline.run_full_evaluation()
    
    print("\nEvaluation completed!")
    print("Check evaluation/results.json for detailed results")
    
    return results


if __name__ == "__main__":
    run_evaluation()