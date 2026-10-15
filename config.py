"""
ResiliRoute Configuration Module
Loads configuration from environment variables or .env file.
"""
import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

# Automatically set GOOGLE_APPLICATION_CREDENTIALS if gcp_service_account.json exists in root
gcp_key_file = Path(__file__).resolve().parent / "gcp_service_account.json"
if gcp_key_file.exists() and "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(gcp_key_file)

class Settings(BaseModel):
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    EKISPERT_API_KEY: str = os.getenv("EKISPERT_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    GEMINI_MODEL_FALLBACK: str = os.getenv("GEMINI_MODEL_FALLBACK", "gemini-flash-latest")
    
    # GCP & Vertex AI settings
    GCP_PROJECT_ID: str = os.getenv("VERTEX_AI_PROJECT_ID", "gen-lang-client-0714733682")
    VERTEX_AI_PROJECT_ID: str = os.getenv("VERTEX_AI_PROJECT_ID", "gen-lang-client-0714733682")
    VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "asia-northeast1")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", str(gcp_key_file))

    # Cache Adapter: "local" (in-memory LRU, $0) or "vertex_ai" (Enterprise)
    CACHE_BACKEND: str = os.getenv("CACHE_BACKEND", "local")
    
    # Slack Integration (Optional webhook)
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

    # Server settings
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    # Ekispert API Base URL
    EKISPERT_BASE_URL: str = "https://api.ekispert.jp/v1/json"

settings = Settings()
