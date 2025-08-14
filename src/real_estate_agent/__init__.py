"""🏠 Real Estate AI Agent with GPT-5 and Pinecone hybrid search."""

__version__ = "0.1.0"
__author__ = "Real Estate AI Team"
__email__ = "contact@realestate-ai.com"

from .schemas import PropertyMetadata, PropertyListing
from .config import Settings

__all__ = [
    "PropertyMetadata",
    "PropertyListing", 
    "Settings",
]