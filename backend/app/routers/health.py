from fastapi import APIRouter
from ..services.health_check import health_check_service
from ..schemas.health import FullHealthReport

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_status():
    """
    Quick health check - returns 200 OK if service is running.
    """
    return {
        "status": "online",
        "project": "InsightStream AI",
        "version": "0.2.0"
    }

@router.get("/services")
async def check_all_services() -> FullHealthReport:
    """
    Full health report for all external services:
    - Groq API
    - Google Gemini
    - Qdrant
    - Supabase
    - RabbitMQ
    - Ollama (fallback)

    Returns detailed status for each service.
    """
    report = await health_check_service.get_full_report()
    return report

@router.get("/groq")
async def check_groq():
    """Check Groq API availability for summarization"""
    return await health_check_service.check_groq()

@router.get("/gemini")
async def check_gemini():
    """Check Google Gemini API availability for embeddings"""
    return await health_check_service.check_google_gemini()

@router.get("/qdrant")
async def check_qdrant():
    """Check Qdrant vector database availability"""
    return await health_check_service.check_qdrant()

@router.get("/supabase")
async def check_supabase():
    """Check Supabase (PostgreSQL) availability"""
    return await health_check_service.check_supabase()

@router.get("/rabbitmq")
async def check_rabbitmq():
    """Check RabbitMQ message broker availability"""
    return await health_check_service.check_rabbitmq()

@router.get("/ollama")
async def check_ollama():
    """Check Ollama local fallback availability"""
    return await health_check_service.check_ollama()
