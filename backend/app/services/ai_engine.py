from google import genai
from google.genai import types
from groq import Groq
from ..core.config import settings
from .ollama_fallback import ollama_fallback

class AIEngine:
    def __init__(self):
        # 1. חיבור ל-Google (הגרסה החדשה)
        self.google_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        
        # 2. חיבור ל-Groq
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)

    def get_embedding(self, text: str) -> list[float]:
        """
        הופך טקסט למספרים (וקטור) באמצעות המודל הזמין בחשבון
        """
        # מנקים רווחים מיותרים
        text = text.replace("\n", " ")
        
        # שימוש במודל שנמצא זמין בחשבון שלך
        result = self.google_client.models.embed_content(
            model="models/gemini-embedding-001", # <-- השינוי כאן
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )
        return result.embeddings[0].values

    async def summarize_article(self, text: str) -> str:
        """
        Summarize article using Groq (primary) or Ollama (fallback).
        Tries Groq first. If it fails (token limit, rate limit, etc.),
        falls back to local Ollama model.
        """
        prompt = f"""
        You are an expert tech analyst. Summarize the following news article into a concise,
        informative paragraph in Hebrew. Focus on the main innovation or business impact.

        Article:
        {text[:10000]}
        """

        # Try Groq first
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )
            summary = response.choices[0].message.content
            print(f"✅ Groq summarization successful")
            return summary
        except Exception as groq_error:
            print(f"⚠️ Groq failed: {str(groq_error)}")
            print("🔄 Attempting Ollama fallback...")

            # Fallback to Ollama
            ollama_summary = await ollama_fallback.summarize(text)
            if ollama_summary:
                print(f"✅ Ollama fallback successful")
                return ollama_summary

            # If both fail, return a placeholder
            print(f"❌ Both Groq and Ollama failed")
            return f"Unable to generate summary. Error: {str(groq_error)[:100]}"

# יצירת מופע יחיד של המנוע
ai_engine = AIEngine()