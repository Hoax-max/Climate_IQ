"""
Configuration settings for Climate Action Intelligence Platform
"""
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # IBM watsonx.ai Configuration
    IBM_CLOUD_API_KEY: str = os.getenv("IBM_CLOUD_API_KEY", "")
    WATSONX_PROJECT_ID: str = os.getenv("WATSONX_PROJECT_ID", "")
    IBM_CLOUD_URL: str = os.getenv("IBM_CLOUD_URL", "https://us-south.ml.cloud.ibm.com")
    WATSONX_API_KEY: str = os.getenv("WATSONX_API_KEY", "")
    
    # Climate Data APIs
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    OPENWEATHER_API_BASE: str = os.getenv("OPENWEATHER_API_BASE", "https://api.openweathermap.org/data/2.5")
    
    NASA_API_KEY: str = os.getenv("NASA_API_KEY", "")
    NASA_API_BASE: str = os.getenv("NASA_API_BASE", "https://power.larc.nasa.gov/api/temporal")
    
    CARBON_INTERFACE_API_KEY: str = os.getenv("CARBON_INTERFACE_API_KEY", "")
    CARBON_INTERFACE_API_BASE: str = os.getenv("CARBON_INTERFACE_API_BASE", "https://www.carboninterface.com/api/v1")
    
    CLIMATETRACE_API_BASE: str = os.getenv("CLIMATETRACE_API_BASE", "https://api.climatetrace.org/v6")
    CLIMATETRACE_DOCS_URL: str = os.getenv("CLIMATETRACE_DOCS_URL", "https://api.climatetrace.org/v6/swagger/index.html")
    
    UN_SDG_API_BASE: str = os.getenv("UN_SDG_API_BASE", "https://unstats.un.org/SDGAPI/v1")
    UN_SDG_SWAGGER_URL: str = os.getenv("UN_SDG_SWAGGER_URL", "https://unstats.un.org/SDGAPI/swagger/")
    WORLD_BANK_API_BASE: str = os.getenv("WORLD_BANK_API_BASE", "https://api.worldbank.org/v2")
    
    # Application Settings
    DEFAULT_OUTPUT_FORMAT: str = os.getenv("DEFAULT_OUTPUT_FORMAT", "json")
    
    # Vector Database Settings
    CHROMA_PERSIST_DIRECTORY: str = "./data/climate_vectordb"
    
    # Model Settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    WATSONX_MODEL_ID: str = "ibm/granite-13b-instruct-v2"  # IBM Granite model for hackathon
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()