from pydantic import ConfigDict
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = ConfigDict(env_file = ".env")

    database_url:str = r'sqlite:///./budget.db'
    app_title:str = r'Family Budget API'
    debug: bool = True

settings = Settings()

