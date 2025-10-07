from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # MongoDB
    mongo_url: str = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    db_name: str = os.getenv('DB_NAME', 'polymailer_db')
    
    # JWT
    jwt_secret: str = os.getenv('JWT_SECRET', 'change-me-in-production')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM', 'HS256')
    access_token_expire_minutes: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    refresh_token_expire_days: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    
    # App
    app_url: str = os.getenv('APP_URL', 'http://localhost:3000')
    api_url: str = os.getenv('API_URL', 'http://localhost:8000/api')
    
    # Stripe
    stripe_public_key: str = os.getenv('STRIPE_PUBLIC_KEY', '')
    stripe_secret_key: str = os.getenv('STRIPE_SECRET_KEY', '')
    stripe_webhook_secret: str = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    # Email
    sendgrid_api_key: str = os.getenv('SENDGRID_API_KEY', '')
    sender_email: str = os.getenv('SENDER_EMAIL', 'orders@polymailer.com')
    
    # Google OAuth
    google_client_id: str = os.getenv('GOOGLE_CLIENT_ID', '')
    google_client_secret: str = os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    # Storage
    upload_dir: str = os.getenv('UPLOAD_DIR', './uploads')
    max_upload_mb: int = int(os.getenv('MAX_UPLOAD_MB', '10'))
    
    # GST
    gst_percent: float = float(os.getenv('GST_PERCENT', '9'))
    default_currency: str = os.getenv('DEFAULT_CURRENCY', 'SGD')
    
    # CORS
    cors_origins: str = os.getenv('CORS_ORIGINS', '*')
    
    # Emergent AI
    emergent_llm_key: str = os.getenv('EMERGENT_LLM_KEY', '')
    
    class Config:
        env_file = '.env'

settings = Settings()
