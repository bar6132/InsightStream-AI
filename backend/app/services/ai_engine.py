from google import genai
from google.genai import types
from groq import Groq
from ..core.config import settings

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
        מסכם מאמר ארוך באמצעות המודל ה"כבד" והחכם (Llama 3 70B)
        """
        prompt = f"""
        You are an expert tech analyst. Summarize the following news article into a concise, 
        informative paragraph in Hebrew. Focus on the main innovation or business impact.
        
        Article:
        {text[:10000]} 
        """
        
        response = self.groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )
        return response.choices[0].message.content

# יצירת מופע יחיד של המנוע
ai_engine = AIEngine()