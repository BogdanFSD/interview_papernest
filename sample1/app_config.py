import os
from dotenv import load_dotenv

# Load environment variables from a .env file (for local development)
load_dotenv()

class Config:
    TESTING = False
    DEBUG = True
    POSTGRES_DB = os.getenv("POSTGRES_DB", "network_db")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres_container")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)

class TestingConfig(Config):
    TESTING = True
    POSTGRES_DB = "test_network_db"
