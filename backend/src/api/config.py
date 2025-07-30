from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    VLLM_API_BASE_URL: str
    VLLM_MODEL_NAME: str
    DATABASE_URL: str
    QDRANT_URL: str # Ajouté pour la cohérence

settings = Settings()