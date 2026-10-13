from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import secrets


class Settings(BaseSettings):
    # App
    APP_NAME: str = "cobalt-forge"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./cobalt_forge.db"

    # Security
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Keycloak / OIDC
    OIDC_ISSUER_URL: str = "http://localhost:8080/realms/cobalt-forge"
    OIDC_CLIENT_ID: str = "cobalt-forge"
    OIDC_CLIENT_SECRET: str = ""
    OIDC_REDIRECT_URI: str = "http://localhost:3000/callback"
    OIDC_SCOPES: str = "openid profile email"

    # LLM (optional)
    LLM_API_KEY: Optional[str] = None
    LLM_PROVIDER: Optional[str] = None  # openai-compatible, anthropic, gemini, ollama
    LLM_MODEL: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None
    LLM_TIMEOUT_SECONDS: int = 30

    # Frontend URL (for CORS)
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()