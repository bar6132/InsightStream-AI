import httpx
import os
from typing import Optional


class OllamaFallbackService:
    """
    Local Ollama service with two dedicated models:
    - llama3.1:8b  → article summarization in Hebrew (better language quality)
    - mistral:7b   → agent reasoning, JSON output (strict instruction following)
    """

    SUMMARIZATION_MODEL = "llama3.1:8b"
    REASONING_MODEL = "mistral:7b"

    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.is_available = False
        # Keep .model for backward compatibility with llama_agent.py
        self.model = self.REASONING_MODEL

    async def _get_loaded_models(self) -> list[str]:
        """Return list of model names currently available in Ollama."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    tags = response.json()
                    return [m.get("name", "") for m in tags.get("models", [])]
        except Exception:
            pass
        return []

    async def check_health(self) -> bool:
        """
        Check if both required models are available.
        Sets is_available=True if at least the reasoning model is ready.
        """
        try:
            models = await self._get_loaded_models()
            has_reasoning = any(self.REASONING_MODEL in m for m in models)
            has_summarization = any(self.SUMMARIZATION_MODEL in m for m in models)

            self.is_available = has_reasoning
            print(f"🔍 Ollama models — {self.REASONING_MODEL}: {'✅' if has_reasoning else '❌'} | {self.SUMMARIZATION_MODEL}: {'✅' if has_summarization else '❌'}")
            return self.is_available
        except Exception as e:
            print(f"❌ Ollama health check failed: {e}")
            self.is_available = False
            return False

    async def pull_model(self) -> bool:
        """Pull both models if not already present."""
        models = await self._get_loaded_models()
        success = True

        for model in [self.REASONING_MODEL, self.SUMMARIZATION_MODEL]:
            if any(model in m for m in models):
                print(f"✅ Model '{model}' already present")
                continue
            try:
                async with httpx.AsyncClient(timeout=600.0) as client:
                    print(f"📥 Pulling '{model}'...")
                    response = await client.post(
                        f"{self.base_url}/api/pull",
                        json={"name": model},
                        timeout=600.0
                    )
                    if response.status_code == 200:
                        print(f"✅ '{model}' ready")
                    else:
                        print(f"❌ Failed to pull '{model}'")
                        success = False
            except Exception as e:
                print(f"❌ Pull error for '{model}': {e}")
                success = False

        self.is_available = success
        return success

    async def _generate(self, model: str, prompt: str, temperature: float = 0.5, timeout: float = 90.0) -> Optional[str]:
        """Send a prompt to a specific Ollama model and return the response."""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "temperature": temperature,
                    }
                )
                if response.status_code == 200:
                    result = response.json().get("response", "").strip()
                    return result if result else None
        except Exception as e:
            print(f"❌ Ollama generate failed ({model}): {e}")
            return None

    async def summarize(self, text: str) -> Optional[str]:
        """
        Summarize article in Hebrew using llama3.1:8b.
        Falls back to reasoning model if summarization model unavailable.
        """
        if not self.is_available:
            return None

        models = await self._get_loaded_models()
        model = self.SUMMARIZATION_MODEL if any(self.SUMMARIZATION_MODEL in m for m in models) else self.REASONING_MODEL

        prompt = f"""Summarize the following news article into a concise, informative paragraph in Hebrew.
Focus on the main innovation or business impact. Keep it under 100 words.

Article:
{text[:8000]}

Summary:"""

        result = await self._generate(model, prompt, temperature=0.5, timeout=90.0)
        if result:
            print(f"✅ Ollama summarization successful ({model})")
        return result

    async def reason(self, prompt: str, temperature: float = 0.3, timeout: float = 45.0) -> Optional[str]:
        """
        Send a reasoning/agent prompt to mistral:7b.
        Used by the Llama agent for topic selection and query generation.
        """
        if not self.is_available:
            return None
        return await self._generate(self.REASONING_MODEL, prompt, temperature=temperature, timeout=timeout)


# Singleton instance
ollama_fallback = OllamaFallbackService()
