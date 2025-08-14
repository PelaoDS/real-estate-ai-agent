"""Pinecone client for real estate property search."""

from typing import List, Dict, Any, Optional
from loguru import logger
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

from .config import settings
from .schemas import PropertyListing


class PineconeClient:
    """Client for managing Pinecone operations for real estate data."""
    
    def __init__(self):
        """Initialize Pinecone client and vector store."""
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = settings.pinecone_index_name
        self.index = None
        self.vector_store = None
        self.embeddings = None
        
        self._setup_embeddings()
        self._setup_index()
        self._setup_vector_store()
    
    def _setup_embeddings(self):
        """Setup OpenAI embeddings."""
        logger.info(f"Setting up OpenAI embeddings with model: {settings.embedding_model}")
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.embedding_model,
            dimensions=settings.embedding_dimension
        )
    
    def _setup_index(self):
        """Setup or create Pinecone index."""
        try:
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=settings.pinecone_dimension,
                    metric=settings.pinecone_metric,
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.pinecone_environment
                    )
                )
                logger.info(f"Successfully created index: {self.index_name}")
            else:
                logger.info(f"Using existing Pinecone index: {self.index_name}")
            
            # Get index reference
            self.index = self.pc.Index(self.index_name)
            
        except Exception as e:
            logger.error(f"Error setting up Pinecone index: {str(e)}")
            raise
    
    def _setup_vector_store(self):
        """Setup LangChain Pinecone vector store."""
        try:
            logger.info("Setting up LangChain Pinecone vector store")
            self.vector_store = PineconeVectorStore(
                index=self.index,
                embedding=self.embeddings,
                text_key="searchable_content",  # Field containing the text to embed
                namespace=""  # Default namespace
            )
            logger.info("Successfully initialized vector store")
            
        except Exception as e:
            logger.error(f"Error setting up vector store: {str(e)}")
            raise
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.total_vector_count,
                "index_fullness": stats.index_fullness,
                "namespaces": stats.namespaces
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {}\n    
    def upsert_property(self, property_listing: PropertyListing) -> bool:
        """
        Upsert a single property listing to Pinecone.
        
        Args:
            property_listing: PropertyListing object to insert/update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get searchable content for embedding
            searchable_content = property_listing.get_searchable_content()
            
            # Prepare document for vector store
            documents = [searchable_content]
            metadatas = [property_listing.to_dict_for_pinecone()["metadata"]]
            ids = [property_listing.metadata.property_id]
            
            # Add to vector store
            self.vector_store.add_texts(
                texts=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully upserted property: {property_listing.metadata.property_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting property {property_listing.metadata.property_id}: {str(e)}")
            return False
    
    def upsert_properties(self, property_listings: List[PropertyListing], batch_size: int = 100) -> Dict[str, int]:
        """
        Upsert multiple property listings to Pinecone in batches.
        
        Args:
            property_listings: List of PropertyListing objects
            batch_size: Number of properties to process in each batch
            
        Returns:
            Dict with success/failure counts
        """
        total_properties = len(property_listings)
        successful_upserts = 0
        failed_upserts = 0
        
        logger.info(f"Starting batch upsert of {total_properties} properties")
        
        for i in range(0, total_properties, batch_size):
            batch = property_listings[i:i + batch_size]
            batch_texts = []
            batch_metadatas = []
            batch_ids = []
            
            # Prepare batch data
            for property_listing in batch:
                try:
                    batch_texts.append(property_listing.get_searchable_content())
                    batch_metadatas.append(property_listing.to_dict_for_pinecone()["metadata"])
                    batch_ids.append(property_listing.metadata.property_id)
                except Exception as e:
                    logger.error(f"Error preparing property {property_listing.metadata.property_id}: {str(e)}")
                    failed_upserts += 1
                    continue
            
            # Upsert batch
            try:
                if batch_texts:  # Only upsert if we have valid data
                    self.vector_store.add_texts(
                        texts=batch_texts,
                        metadatas=batch_metadatas,
                        ids=batch_ids
                    )
                    successful_upserts += len(batch_texts)
                    logger.info(f"Batch {i//batch_size + 1}: Upserted {len(batch_texts)} properties")
                
            except Exception as e:
                logger.error(f"Error upserting batch {i//batch_size + 1}: {str(e)}")
                failed_upserts += len(batch_texts)
        
        result = {
            "total": total_properties,
            "successful": successful_upserts,
            "failed": failed_upserts
        }
        
        logger.info(f"Batch upsert completed: {result}")
        return result
    
    def search_properties(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
        namespace: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Search for properties using semantic similarity and metadata filters.
        
        Args:
            query: Natural language search query
            filters: Metadata filters in Pinecone format
            top_k: Number of results to return
            namespace: Pinecone namespace to search
            
        Returns:
            List of matching properties with scores
        """
        try:
            logger.info(f"Searching properties with query: '{query}', filters: {filters}")
            
            # Perform similarity search with metadata filtering
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=top_k,
                filter=filters,
                namespace=namespace
            )
            
            # Format results
            formatted_results = []
            for doc, score in results:
                result = {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "similarity_score": score,
                }
                formatted_results.append(result)
            
            logger.info(f"Found {len(formatted_results)} matching properties")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching properties: {str(e)}")
            return []
    
    def delete_property(self, property_id: str, namespace: str = "") -> bool:
        """
        Delete a property by ID.
        
        Args:
            property_id: Unique property identifier
            namespace: Pinecone namespace
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.vector_store.delete(ids=[property_id], namespace=namespace)
            logger.info(f"Successfully deleted property: {property_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting property {property_id}: {str(e)}")
            return False
    
    def clear_all_properties(self, namespace: str = "") -> bool:
        """
        Clear all properties from the index (use with caution!).
        
        Args:
            namespace: Pinecone namespace to clear
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            logger.warning(f"Cleared all properties from namespace: '{namespace}'")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing properties: {str(e)}")
            return False
    
    def build_price_filter(self, min_price: Optional[int] = None, max_price: Optional[int] = None) -> Dict[str, Any]:
        """Build price range filter for Pinecone."""
        price_filter = {}
        
        if min_price is not None and max_price is not None:
            price_filter = {
                "$and": [
                    {"price": {"$gte": min_price}},
                    {"price": {"$lte": max_price}}
                ]
            }
        elif min_price is not None:
            price_filter = {"price": {"$gte": min_price}}
        elif max_price is not None:
            price_filter = {"price": {"$lte": max_price}}
        
        return price_filter
    
    def build_metadata_filter(self, **filters) -> Dict[str, Any]:
        """
        Build complex metadata filter for Pinecone search.
        
        Args:
            **filters: Keyword arguments for filtering
            
        Returns:
            Dict: Pinecone-compatible filter
        """
        filter_conditions = []
        
        # Property type filter
        if "property_type" in filters and filters["property_type"]:
            filter_conditions.append({"property_type": {"$eq": filters["property_type"]}})
        
        # Location filters
        if "city" in filters and filters["city"]:
            filter_conditions.append({"city": {"$eq": filters["city"]}})
        
        if "state" in filters and filters["state"]:
            filter_conditions.append({"state": {"$eq": filters["state"]}})
        
        if "neighborhood" in filters and filters["neighborhood"]:
            filter_conditions.append({"neighborhood": {"$eq": filters["neighborhood"]}})
        
        # Bedroom/bathroom filters
        if "min_bedrooms" in filters and filters["min_bedrooms"] is not None:
            filter_conditions.append({"bedrooms": {"$gte": filters["min_bedrooms"]}})
        
        if "min_bathrooms" in filters and filters["min_bathrooms"] is not None:
            filter_conditions.append({"bathrooms": {"$gte": filters["min_bathrooms"]}})
        
        # Price filter
        price_filter = self.build_price_filter(
            filters.get("min_price"), 
            filters.get("max_price")
        )
        if price_filter:
            filter_conditions.append(price_filter)
        
        # Amenities filter (property must have ALL required amenities)
        if "required_amenities" in filters and filters["required_amenities"]:
            for amenity in filters["required_amenities"]:
                filter_conditions.append({"amenities": {"$in": [amenity]}})
        
        # Property status filter (default to active)
        status = filters.get("status", "active")
        filter_conditions.append({"status": {"$eq": status}})
        
        # Combine all conditions with AND
        if len(filter_conditions) == 1:
            return filter_conditions[0]
        elif len(filter_conditions) > 1:
            return {"$and": filter_conditions}
        else:
            return {}


# Global client instance
pinecone_client = PineconeClient()