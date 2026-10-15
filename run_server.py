"""
ResiliRoute Entry Point Runner Script
Starts the FastAPI server with Uvicorn.
"""
import sys
import uvicorn

# Configure UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import settings

def main():
    print("=" * 70)
    print(" [*] Starting ResiliRoute BCP Mobility Orchestrator v3.3")
    print("=" * 70)
    print(f" - Host: http://{settings.HOST}:{settings.PORT}")
    print(f" - API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    print(f" - Web Control Center: http://{settings.HOST}:{settings.PORT}/")
    print(f" - Cache Backend: {settings.CACHE_BACKEND} (Local Memory $0.00 / Vertex AI)")
    print(f" - Gemini Model: {settings.GEMINI_MODEL} (Fallback: {settings.GEMINI_MODEL_FALLBACK})")
    print(f" - Ekispert Key: Active ({settings.EKISPERT_API_KEY[:4]}****)")
    print("=" * 70)

    uvicorn.run(
        "server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    main()
