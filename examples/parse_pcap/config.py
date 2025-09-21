import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration settings for the traffic parser application."""
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///traffic_data.db')
    
    # Directory settings
    PCAP_DIRECTORY = os.getenv('PCAP_DIRECTORY', './pcap_files')
    OUTPUT_JSON_FILE = os.getenv('OUTPUT_JSON_FILE', './traffic_export.json')
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Processing settings
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '1000'))
    MAX_PACKETS_PER_FILE = int(os.getenv('MAX_PACKETS_PER_FILE', '10000'))
