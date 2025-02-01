from pydantic_settings import BaseSettings
from pydantic import Field 



class Config(BaseSettings):
    OPENAI_API_KEY: str = Field(..., env='OPENAI_API_KEY')


