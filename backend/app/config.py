from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://credituser:creditpass@localhost:5432/credit_scoring"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # Model paths

    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    MODEL_PATH: str = str(BASE_DIR / "models" / "xgboost_model.pkl")
    SHAP_EXPLAINER_PATH: str = str(BASE_DIR / "models" / "shap_explainer.pkl")
    FEATURE_NAMES_PATH: str = str(BASE_DIR / "models" / "feature_names.pkl")
        
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:3000",
    "https://edi-4.vercel.app"
]
    
    # Application
    PROJECT_NAME: str = "AI Credit Scoring Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Email
    GMAIL_ADDRESS: str = ""
    GMAIL_APP_PASSWORD: str = ""
    FRONTEND_URL: str = "https://edi-4.vercel.app"
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
