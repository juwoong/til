from pydantic_settings import BaseSettings
from pydantic import Field 


class Config(BaseSettings):
    OPENAI_API_KEY: str = Field(..., env='OPENAI_API_KEY')
    DB_HOST: str = Field(..., env='DB_HOST')
    DB_PORT: int = Field(..., env='DB_PORT')
    DB_USER: str = Field(..., env='DB_USER')
    DB_PASSWORD: str = Field(..., env='DB_PASSWORD')
    DB_NAME: str = Field(..., env='DB_NAME')
    
