"""Real Estate AI Agent with GPT-5 and search tools (MVP)."""

from typing import List, Dict, Any, Optional, Type
from loguru import logger
from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_tool_calling_agent  # Updated for GPT-5
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import Field

from .config import settings
from .pinecone_client import pinecone_client


class PropertySearchTool(BaseTool):
    """Tool for searching properties with semantic search and filters."""
    
    name: str = Field(default="search_properties")
    description: str = Field(default="""
    Search for real estate properties using semantic search and metadata filters.
    
    Parameters:
    - query (str): Semantic search query describing what the user is looking for
    - filters (dict, optional): Metadata filters. Supported filters:
        - property_type: "house", "apartment", "condo", "townhouse", "studio"
        - city: City name (e.g., "New York", "Miami")
        - state: State abbreviation (e.g., "NY", "FL")
        - neighborhood: Neighborhood name
        - min_price: Minimum price in USD
        - max_price: Maximum price in USD  
        - min_bedrooms: Minimum number of bedrooms
        - min_bathrooms: Minimum number of bathrooms
        - required_amenities: List of amenities like ["pool", "gym", "parking"]
    - top_k (int, optional): Max results to return (default: 10)
    
    Example:
    search_properties("modern apartment with city views", {"city": "Miami", "min_bedrooms": 2, "max_price": 500000})
    """)
    
    def _run(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        top_k: int = 10,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> List[Dict[str, Any]]:
        """Execute property search."""
        try:
            logger.info(f"Searching: query='{query}', filters={filters}")
            
            # Build Pinecone filters
            pinecone_filters = {}
            if filters:
                pinecone_filters = pinecone_client.build_metadata_filter(**filters)
            
            # Search
            results = pinecone_client.search_properties(
                query=query,
                filters=pinecone_filters,
                top_k=top_k
            )
            
            # Format for agent
            formatted_results = []
            for result in results:
                metadata = result.get('metadata', {})
                formatted_results.append({
                    'property_id': metadata.get('property_id', 'N/A'),
                    'title': metadata.get('title', 'N/A'),
                    'price': f"${metadata.get('price', 0):,}",
                    'bedrooms': metadata.get('bedrooms', 'N/A'),
                    'bathrooms': metadata.get('bathrooms', 'N/A'),
                    'square_feet': f"{metadata.get('square_feet', 0):,} sq ft",
                    'property_type': metadata.get('property_type', 'N/A'),
                    'city': metadata.get('city', 'N/A'),
                    'state': metadata.get('state', 'N/A'),
                    'neighborhood': metadata.get('neighborhood', 'N/A'),
                    'amenities': metadata.get('amenities', []),
                    'description': metadata.get('description', 'N/A')[:150] + '...',
                    'price_per_sqft': f"${metadata.get('price_per_sqft', 0):.0f}/sq ft",
                    'year_built': metadata.get('year_built', 'N/A'),
                    'days_on_market': metadata.get('days_on_market', 'N/A'),
                    'similarity_score': f"{result.get('similarity_score', 0):.3f}"
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []


class GetIndexStatsTool(BaseTool):
    """Tool for getting database statistics."""
    
    name: str = Field(default="get_database_stats")
    description: str = Field(default="Get statistics about the property database including total number of properties.")
    
    def _run(
        self, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Get database stats."""
        try:
            stats = pinecone_client.get_index_stats()
            return {
                "total_properties": stats.get("total_vectors", 0),
                "status": "healthy" if stats else "error"
            }
        except Exception as e:
            logger.error(f"Stats error: {str(e)}")
            return {"status": "error", "message": str(e)}


class RealEstateAgent:
    """GPT-5 powered real estate agent with search capabilities."""
    
    def __init__(self):
        """Initialize the agent with GPT-5 and tools."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,  # Will use gpt-4o for now
            # temperature=settings.openai_temperature, #temperatura default
            max_tokens=settings.openai_max_tokens,
            openai_api_key=settings.openai_api_key,
            streaming=False  # Disable streaming for better compatibility
        )
        
        # Available tools
        self.tools = [
            PropertySearchTool(),
            GetIndexStatsTool()
        ]
        
        # System prompt for the agent
        self.system_prompt = """You are an expert real estate agent. You help clients find their dream properties using a comprehensive property database.

Your capabilities:
- Search properties using semantic understanding and filters
- Analyze property data and provide insights
- Compare properties and make recommendations
- Answer questions about market trends and property details

Guidelines:
- Always be helpful, professional, and knowledgeable
- When searching, think about what filters would be most relevant
- Provide detailed explanations and comparisons when presenting properties
- If you need to search, explain your search strategy
- Format property information clearly with prices, locations, and key details
- Suggest alternatives if the exact request isn't available

Use your tools to search the database and provide comprehensive responses."""

        # Create the agent
        self._setup_agent()
    
    def _setup_agent(self):
        """Setup the LangChain agent with tools."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # Use create_tool_calling_agent for better GPT-5 compatibility
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    def search_properties(self, user_query: str) -> str:
        """
        Process a user query and return property search results with analysis.
        
        Args:
            user_query: Natural language query from the user
            
        Returns:
            Formatted response with property results and analysis
        """
        try:
            logger.info(f"Processing user query: '{user_query}'")
            
            # Let the agent decide how to search and respond
            response = self.agent_executor.invoke({"input": user_query})
            
            return response.get("output", "I couldn't process your request at this time.")
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return f"I encountered an error while searching for properties: {str(e)}"
    
    def get_database_info(self) -> str:
        """Get information about the property database."""
        try:
            response = self.agent_executor.invoke({
                "input": "What information can you tell me about the property database?"
            })
            return response.get("output", "Unable to retrieve database information.")
        except Exception as e:
            logger.error(f"Error getting database info: {str(e)}")
            return f"Error retrieving database information: {str(e)}"


# Global agent instance
real_estate_agent = RealEstateAgent()