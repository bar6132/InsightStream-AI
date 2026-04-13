from typing import Dict, Optional, Any
from datetime import datetime
import httpx
import os
import asyncio
from groq import Groq
from google import genai
from ..core.database import supabase, qdrant
from ..core.config import settings
from .ollama_fallback import ollama_fallback

class HealthCheckService:
    """
    Monitors health of all external services:
    - Groq API (summarization)
    - Google Gemini (embeddings)
    - Qdrant (vector database)
    - Supabase (PostgreSQL + Auth)
    - RabbitMQ (message broker)
    - Ollama (local fallback)

    NOTE: Some check methods use synchronous API calls (Groq, Gemini, Qdrant, Supabase).
    This is acceptable for health checks which are:
    - Infrequent (not on every request)
    - Short-lived (< 5s each)
    - Parallel-safe (run concurrently via asyncio.gather)

    For true async operations, these libraries would need async client variants.
    """

    async def check_groq(self) -> Dict[str, Any]:
        """Check Groq API availability"""
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10,
                timeout=10
            )
            return {
                "status": "healthy",
                "service": "Groq",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "Groq",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_google_gemini(self) -> Dict[str, Any]:
        """Check Google Gemini API availability"""
        try:
            client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            result = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents="health check",
                timeout=10
            )
            if result.embeddings:
                return {
                    "status": "healthy",
                    "service": "Google Gemini",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "service": "Google Gemini",
                    "error": "No embeddings returned",
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "Google Gemini",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_qdrant(self) -> Dict[str, Any]:
        """Check Qdrant vector database availability"""
        try:
            collection_info = qdrant.get_collection(
                "news_vectors",
                timeout=10
            )
            return {
                "status": "healthy",
                "service": "Qdrant",
                "points_count": collection_info.points_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "Qdrant",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_supabase(self) -> Dict[str, Any]:
        """Check Supabase (PostgreSQL + Auth) availability"""
        try:
            response = supabase.table("news_articles").select("id").limit(1).execute()
            return {
                "status": "healthy",
                "service": "Supabase",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "Supabase",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_rabbitmq(self) -> Dict[str, Any]:
        """Check RabbitMQ availability"""
        try:
            import aio_pika
            url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
            connection = await aio_pika.connect_robust(url, timeout=5)
            await connection.close()
            return {
                "status": "healthy",
                "service": "RabbitMQ",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "RabbitMQ",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def check_ollama(self) -> Dict[str, Any]:
        """Check Ollama local fallback availability"""
        try:
            is_available = await ollama_fallback.check_health()
            return {
                "status": "healthy" if is_available else "unhealthy",
                "service": "Ollama (Local Fallback)",
                "available": is_available,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": "Ollama (Local Fallback)",
                "error": str(e),
                "available": False,
                "timestamp": datetime.utcnow().isoformat()
            }

    async def get_full_report(self) -> Dict[str, Any]:
        """Get comprehensive health report for all services"""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "services": {}
        }

        checks = [
            self.check_groq(),
            self.check_google_gemini(),
            self.check_qdrant(),
            self.check_supabase(),
            self.check_rabbitmq(),
            self.check_ollama()
        ]

        results = await asyncio.gather(*checks, return_exceptions=True)

        healthy_count = 0
        for result in results:
            if isinstance(result, dict):
                service = result.get("service", "Unknown")
                status = result.get("status", "unknown")
                report["services"][service] = result
                if status == "healthy":
                    healthy_count += 1

        report["summary"] = {
            "total_services": len(results),
            "healthy": healthy_count,
            "unhealthy": len(results) - healthy_count,
            "status": "all_healthy" if healthy_count == len(results) else "degraded"
        }

        return report

# Singleton instance
health_check_service = HealthCheckService()
