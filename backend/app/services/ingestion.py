import feedparser
import uuid
from datetime import datetime
from ..core.database import supabase, qdrant
from ..services.ai_engine import ai_engine
from qdrant_client.models import PointStruct

# רשימת מקורות להדגמה (אפשר להוסיף עוד)
RSS_FEEDS = [
    "http://feeds.feedburner.com/TechCrunch/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/category/ai/latest/rss"
]

class IngestionService:
    async def run_pipeline(self):
        """
        הפונקציה הראשית שמריצה את כל תהליך האיסוף
        """
        results = {"added": 0, "errors": 0, "skipped": 0}
        print("🚀 Starting Ingestion Pipeline...")

        for feed_url in RSS_FEEDS:
            try:
                # 1. קריאת ה-RSS
                feed = feedparser.parse(feed_url)
                print(f"📥 Parsing: {feed_url} ({len(feed.entries)} items)")

                for entry in feed.entries[:3]: # הגבלה ל-3 כתבות מכל מקור לבדיקה
                    try:
                        await self.process_article(entry)
                        results["added"] += 1
                    except ValueError:
                         results["skipped"] += 1
                    except Exception as e:
                        print(f"❌ Error processing {entry.link}: {e}")
                        results["errors"] += 1
                        
            except Exception as e:
                print(f"❌ Error fetching feed {feed_url}: {e}")

        return results

    async def process_article(self, entry):
        """
        מעבד כתבה בודדת: בדיקת כפילות -> סיכום -> וקטור -> שמירה
        """
        url = entry.link
        title = entry.title

        # 2. בדיקת כפילות ב-Supabase
        # אם הכתבה כבר קיימת, אנחנו מדלגים עליה כדי לחסוך כסף וזמן
        existing = supabase.table("news_articles").select("id").eq("url", url).execute()
        if existing.data:
            raise ValueError("Duplicate article")

        # 3. יצירת תוכן לסיכום (שילוב של כותרת ותקציר מה-RSS)
        # בפרויקט מלא היינו משתמשים ב-Scraper, כאן נסתפק במידע מה-RSS
        raw_text = f"{title}\n\n{entry.get('summary', '')}"
        
        # 4. הפעלת ה-AI (במקביל)
        # מייצרים סיכום בעברית
        summary_he = await ai_engine.summarize_article(raw_text)
        # מייצרים וקטור לחיפוש
        vector = ai_engine.get_embedding(f"{title}: {entry.get('summary', '')}")

        # 5. שמירה ב-Supabase (Metadata)
        article_data = {
            "title": title,
            "url": url,
            "summary": summary_he,
            "source": entry.get("source", {}).get("title", "Unknown"),
            "published_at": datetime.now().isoformat()
        }
        response = supabase.table("news_articles").insert(article_data).execute()
        article_id = response.data[0]['id'] # מקבלים את ה-UUID שנוצר

        # 6. שמירה ב-Qdrant (Vector)
        # אנחנו משתמשים באותו ID כדי לקשר בין הווקטור למידע הטקסטואלי
        qdrant.upsert(
            collection_name="news_vectors",
            points=[
                PointStruct(
                    id=article_id,
                    vector=vector,
                    payload={
                        "title": title,
                        "url": url,
                        "source": article_data["source"]
                    }
                )
            ]
        )
        print(f"✅ Saved: {title[:30]}...")

ingestion_service = IngestionService()