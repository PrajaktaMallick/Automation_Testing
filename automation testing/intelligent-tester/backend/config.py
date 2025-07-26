"""
Configuration settings for the intelligent web tester
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Logging Configuration
    LOG_LEVEL: str = "info"
    
    # MCP Configuration
    MCP_SERVER_URL: Optional[str] = None
    MCP_API_KEY: Optional[str] = None
    MCP_TIMEOUT: int = 30
    MCP_RETRY_ATTEMPTS: int = 3
    MCP_RETRY_DELAY: int = 1
    
    # Server Configuration
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./intelligent_tester.db"
    
    # Playwright Configuration
    HEADLESS: bool = False
    BROWSER_TYPE: str = "chromium"
    DEFAULT_TIMEOUT: int = 30000
    VIEWPORT_WIDTH: int = 1280
    VIEWPORT_HEIGHT: int = 720
    
    # Screenshot and Logging
    SCREENSHOTS_DIR: str = "./screenshots"
    LOGS_DIR: str = "./logs"
    MAX_SCREENSHOT_SIZE: str = "1920x1080"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_CONCURRENT_TESTS: int = 5
    
    # AI Model Configuration
    DEFAULT_MODEL: str = "gpt-4"
    TEMPERATURE: float = 0.1
    MAX_TOKENS: int = 2000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(settings.LOGS_DIR, exist_ok=True)
