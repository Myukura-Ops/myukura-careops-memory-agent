from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_name: str = "MyuKura CareOps Worker"
    phase: str = "0"
    
    # MongoDB connection string (set via environment variable in production)
    mongodb_uri: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
