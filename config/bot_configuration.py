import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class."""
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'weather_api_key_not_set')
    BOT_TOKEN = os.getenv('BOT_TOKEN', 'bot_token_not_set')