from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

class Settings():
    helsinki_lang_codes = {
        'english': 'en',
        'ukrainian': 'uk',
        'german': 'de',
    }

    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")
    use_llm: bool = True
    cohere_model: str = 'command-r-plus'
    db_url: str = os.getenv("DATABASE_URL")




settings = Settings()
