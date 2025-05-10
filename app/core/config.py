from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn
from typing import Optional, List
import os


class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., min_length=32)
    ENCRYPTION_KEY:str = Field(..., min_length=32)
    ALLOWED_HOSTS: List[str] = Field(
        default=[
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "192.168.30.1",
            "6j2q5nl3-8000.uks1.devtunnels.ms"
        ],
        description="List of allowed hostnames/IPs"
    )
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://192.168.30.1:3000",
            "https://6j2q5nl3-8000.uks1.devtunnels.ms"
        ],
        description="CORS allowed origins"
    )
    
   
    # Database Configuration
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="admin")
    POSTGRES_DB: str = Field(default="translation_system")
    POSTGRES_HOST:str = Field(default="localhost")
    POSTGRES_PORT:int = 5433
    DATABASE_URL: str = None

    # Redis Configuration
    REDIS_URL: Optional[RedisDsn] = Field(default="redis://redis:6379/0")

    # Security Configuration
    SECRET_KEY: str ="your-secret-key-here-mustBE-UPTO-THIRTY-TWO-CHARACTERS" #Field(..., min_length=32)  # Required field
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)
    ENCRYPTION_KEY: str="TbQR-Rq7McdO4BgFSRbyx2gy7A3KDAsyitTfLi-ZFkg="

    # Stripe Configuration
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PREMIUM_PRICE_ID: Optional[str] = None

    # Deepseek Configuration
    DEEPSEEK_API_KEY: Optional[str] = "sk-7c272739285e40fd8792537a19da9af9"
    DEEPSEEK_API_URL: str = Field(default="https://api.deepseek.com/v1")

    # Frontend Configuration
    FRONTEND_URL: str = Field(default="http://localhost:3000")

    # Application Settings
    DEBUG: bool = Field(default=True)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    POSTGRES_URI: PostgresDsn = os.getenv("POSTGRES_URI",
                                          "postgresql://user:password@localhost:5432/document_translator")


    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra vars in .env
    )


settings = Settings()