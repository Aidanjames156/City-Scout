import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for CityScout application."""
    
    # API Keys
    CENSUS_API_KEY = os.getenv('CENSUS_API_KEY')
    BLS_API_KEY = os.getenv('BLS_API_KEY')
    
    # Flask configuration
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-key-change-in-production')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # API Endpoints
    CENSUS_BASE_URL = "https://api.census.gov/data"
    BLS_BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    # Default settings
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
