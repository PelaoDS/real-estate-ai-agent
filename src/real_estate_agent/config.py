"""Configuration settings for the Real Estate AI Agent."""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-5"  # Using GPT-5!
    openai_temperature: float = 0.1
    openai_max_tokens: int = 2000
    
    # Pinecone Configuration
    pinecone_api_key: str
    pinecone_environment: str = "us-east-1-aws"
    pinecone_index_name: str = "real-estate-properties"
    pinecone_dimension: int = 1536  # For OpenAI embeddings
    pinecone_metric: str = "cosine"
    
    # Embedding Configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # Search Configuration
    default_top_k: int = 10
    max_distance_km: float = 50.0  # Max distance for proximity searches
    
    # Google Maps (Optional)
    google_maps_api_key: Optional[str] = None
    
    # Application Configuration
    app_name: str = "RealEstateAgent"
    app_version: str = "0.1.0"
    log_level: str = "INFO"
    
    # Business Logic
    max_property_age_days: int = 365  # Only show properties listed within a year
    default_search_radius_km: float = 10.0
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()