import httpx
from typing import Optional

class OllamaFallbackService:
    """
    Local Ollama service for fallback summarization when Groq is unavailable.
    Uses llama2 model (or mistral for faster performance).
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama2"  # Default model (can be switched to "mistral" for speed)
        self.is_available = False

    async def check_health(self) -> bool:
        """
        Check if Ollama service is running and model is loaded.
        Returns True if healthy, False otherwise.
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    tags = response.json()
                    # Check if our model is available
                    models = [m.get("name", "") for m in tags.get("models", [])]
                    self.is_available = any(self.model in m for m in models)
                    return self.is_available
        except Exception as e:
            print(f"❌ Ollama health check failed: {e}")
            self.is_available = False
            return False
        return False

    async def pull_model(self) -> bool:
        """
        Download and cache the Ollama model if not present.
        Only runs once during startup.
        """
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                print(f"📥 Pulling Ollama model '{self.model}'...")
                response = await client.post(
                    f"{self.base_url}/api/pull",
                    json={"name": self.model},
                    timeout=300.0
                )
                if response.status_code == 200:
                    print(f"✅ Model '{self.model}' ready")
                    self.is_available = True
                    return True
        except Exception as e:
            print(f"❌ Failed to pull Ollama model: {e}")
            return False
        return False

    async def summarize(self, text: str) -> Optional[str]:
        """
        Summarize article using local Ollama model.
        Returns summary or None if Ollama is unavailable.
        """
        if not self.is_available:
            return None

        try:
            prompt = f"""Summarize the following news article into a concise, informative paragraph in Hebrew.
Focus on the main innovation or business impact. Keep it under 100 words.

Article:
{text[:8000]}

Summary:"""

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": 0.5
                    }
                )

                if response.status_code == 200:
                    result = response.json()
                    summary = result.get("response", "").strip()
                    return summary if summary else None
        except Exception as e:
            print(f"❌ Ollama summarization failed: {e}")
            return None

        return None

# Singleton instance
ollama_fallback = OllamaFallbackService()
