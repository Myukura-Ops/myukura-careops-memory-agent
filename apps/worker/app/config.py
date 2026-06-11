from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    project_name: str = "MyuKura CareOps Worker"
    phase: str = "0"
    
    # Placeholders for future phases
    mongodb_uri: str = "PHASE_2_PLACEHOLDER"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
