"""LLM-as-a-judge evaluator for agent performance assessment."""

from typing import List, Dict, Any, Optional
from openai import OpenAI
from loguru import logger

from config import settings


class PropertyMatchEvaluator:
    """LLM judge to evaluate if agent results match expected properties."""
    
    def __init__(self, model: str = "gpt-4o"):
        """Initialize evaluator with specified model."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model
        
    def evaluate_search_results(
        self, 
        query: str,
        agent_results: List[Dict[str, Any]], 
        expected_property_ids: List[str],
        expected_properties_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate if agent search results match expected properties.
        
        Args:
            query: Original user query
            agent_results: Results returned by agent
            expected_property_ids: List of expected property IDs
            expected_properties_data: Full data of expected properties
            
        Returns:
            Dict with evaluation results including accuracy score
        """
        try:
            # Extract property IDs from agent results
            returned_property_ids = []
            for result in agent_results:
                if isinstance(result, dict) and 'property_id' in result:
                    returned_property_ids.append(result['property_id'])
                elif isinstance(result, dict) and 'metadata' in result:
                    returned_property_ids.append(result['metadata'].get('property_id', 'Unknown'))
            
            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(
                query=query,
                returned_property_ids=returned_property_ids,
                expected_property_ids=expected_property_ids,
                expected_properties_data=expected_properties_data,
                agent_results=agent_results
            )
            
            # Get LLM judgment
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500
            )
            
            evaluation_text = response.choices[0].message.content
            
            # Parse evaluation results
            evaluation_result = self._parse_evaluation(evaluation_text)
            evaluation_result.update({
                "query": query,
                "returned_property_ids": returned_property_ids,
                "expected_property_ids": expected_property_ids,
                "evaluation_text": evaluation_text
            })
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Error in evaluation: {str(e)}")
            return {
                "accuracy": 0.0,
                "is_correct": False,
                "error": str(e)
            }
    
    def _get_system_prompt(self) -> str:
        """System prompt for LLM judge."""
        return """You are an expert real estate evaluator. Your job is to assess whether a property search agent returned the correct properties for a given query.

Evaluate based on:
1. Did the agent return properties that match the user's requirements?
2. Are the returned properties relevant to the search criteria?
3. Did the agent miss any obvious matches?

Respond in this exact format:
ACCURACY: [0.0 to 1.0]
IS_CORRECT: [True/False]
REASONING: [Brief explanation of why the results are correct/incorrect]

Be strict but fair in your evaluation."""
    
    def _create_evaluation_prompt(
        self,
        query: str,
        returned_property_ids: List[str],
        expected_property_ids: List[str], 
        expected_properties_data: List[Dict[str, Any]],
        agent_results: List[Dict[str, Any]]
    ) -> str:
        """Create evaluation prompt for LLM judge."""
        
        prompt = f"""
USER QUERY: "{query}"

EXPECTED PROPERTIES (Ground Truth):
{self._format_expected_properties(expected_property_ids, expected_properties_data)}

AGENT RETURNED PROPERTIES:
{self._format_agent_results(agent_results)}

RETURNED PROPERTY IDS: {returned_property_ids}
EXPECTED PROPERTY IDS: {expected_property_ids}

Please evaluate if the agent's results correctly match the user's query requirements.
"""
        return prompt
    
    def _format_expected_properties(self, property_ids: List[str], properties_data: List[Dict[str, Any]]) -> str:
        """Format expected properties for evaluation."""
        formatted = []
        for prop_data in properties_data:
            if prop_data.get('property_id') in property_ids:
                formatted.append(
                    f"- {prop_data['property_id']}: {prop_data['title']} "
                    f"(${prop_data['price']:,}, {prop_data['bedrooms']}BR/{prop_data['bathrooms']}BA, "
                    f"{prop_data['city']}, {prop_data['state']})"
                )
        return "\n".join(formatted) if formatted else "No expected properties"
    
    def _format_agent_results(self, agent_results: List[Dict[str, Any]]) -> str:
        """Format agent results for evaluation."""
        if not agent_results:
            return "No properties returned"
        
        formatted = []
        for result in agent_results[:5]:  # Limit to first 5 for brevity
            if isinstance(result, dict):
                property_id = result.get('property_id', 'Unknown')
                title = result.get('title', 'Unknown')
                price = result.get('price', 'Unknown')
                bedrooms = result.get('bedrooms', 'Unknown')
                bathrooms = result.get('bathrooms', 'Unknown')
                city = result.get('city', 'Unknown')
                state = result.get('state', 'Unknown')
                
                formatted.append(
                    f"- {property_id}: {title} "
                    f"({price}, {bedrooms}BR/{bathrooms}BA, {city}, {state})"
                )
        
        return "\n".join(formatted)
    
    def _parse_evaluation(self, evaluation_text: str) -> Dict[str, Any]:
        """Parse LLM evaluation response."""
        try:
            lines = evaluation_text.strip().split('\n')
            
            accuracy = 0.0
            is_correct = False
            reasoning = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith('ACCURACY:'):
                    accuracy_str = line.split(':', 1)[1].strip()
                    accuracy = float(accuracy_str)
                elif line.startswith('IS_CORRECT:'):
                    correct_str = line.split(':', 1)[1].strip()
                    is_correct = correct_str.lower() == 'true'
                elif line.startswith('REASONING:'):
                    reasoning = line.split(':', 1)[1].strip()
            
            return {
                "accuracy": accuracy,
                "is_correct": is_correct,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logger.error(f"Error parsing evaluation: {str(e)}")
            return {
                "accuracy": 0.0,
                "is_correct": False,
                "reasoning": f"Parse error: {str(e)}"
            }