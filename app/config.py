from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # LLM Provider Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    google_api_key: Optional[str] = None
    google_model: str = "gemini-pro"
    
    primary_llm_provider: str = "openai"  # Only OpenAI supported for now
    
    # Vector Database Configuration
    vector_db_path: str = "./vector_db"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Application Configuration
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Document Processing
    max_document_size_mb: int = 50
    chunk_size: int = 1000
    chunk_overlap: int = 200
    
    # RAG Configuration
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_llm_config():
    """Get the configuration for the primary LLM provider."""
    provider = settings.primary_llm_provider.lower()
    
    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        return {
            "provider": "openai",
            "api_key": settings.openai_api_key,
            "model": settings.openai_model
        }
    elif provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        return {
            "provider": "anthropic",
            "api_key": settings.anthropic_api_key,
            "model": settings.anthropic_model
        }
    elif provider == "google":
        if not settings.google_api_key:
            raise ValueError("Google API key not configured")
        return {
            "provider": "google",
            "api_key": settings.google_api_key,
            "model": settings.google_model
        }
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}") 