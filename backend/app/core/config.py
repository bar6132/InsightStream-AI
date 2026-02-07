from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    #Database
    SUPABASE_URL: str
    SUPABASE_KEY: str
    QDRANT_URL: str
    QDRANT_API_KEY: str
    
    #AI Keys
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    
    #App
    DEPLOYMENT_MODE: str = "local" 

    class Config:
        env_file = ".env"
        extra = "ignore" 

settings = Settings()