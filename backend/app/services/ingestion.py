import feedparser
import uuid
from datetime import datetime
from ..core.database import supabase, supabase_admin, qdrant
from ..services.ai_engine import ai_engine
from qdrant_client.models import PointStruct

# --- 1. EXPANDED RSS FEEDS LIST ---
RSS_FEEDS = [
    # --- Tech & AI ---
    "http://feeds.feedburner.com/TechCrunch/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/category/ai/latest/rss",
    
    # --- Israel News (English) ---
    "https://www.jpost.com/rss/rssfeedsheadlines.aspx",  # Jerusalem Post
    "https://www.ynetnews.com/PicServer5/2019/02/10/english/AllNews.xml", # Ynet News
    
    # --- Economy & Finance ---
    "https://en.globes.co.il/webservice/rss/rssfeeder.ashx?folderid=294", # Globes Israel
    "https://feeds.bloomberg.com/markets/news.rss", # Bloomberg
    
    # --- Science & World ---
    "https://www.sciencedaily.com/rss/top_news.xml",
    "http://feeds.bbci.co.uk/news/rss.xml"
]

class IngestionService:
    async def run_pipeline(self):
        """
        Main entry point: Fetches, Summarizes, Vectorizes, and Saves.
        """
        results = {"added": 0, "errors": 0, "skipped": 0}
        print("🚀 Starting Enhanced Ingestion Pipeline...")

        for feed_url in RSS_FEEDS:
            try:
                # 1. Parse the RSS Feed
                feed = feedparser.parse(feed_url)
                
                # Extract Source Name
                source_name = feed.feed.get("title", "Unknown Source")
                print(f"📥 Parsing: {source_name} ({len(feed.entries)} items)")

                # Limit to 5 articles per feed
                for entry in feed.entries[:5]: 
                    try:
                        await self.process_article(entry, source_name)
                        results["added"] += 1
                    except ValueError:
                         results["skipped"] += 1
                    except Exception as e:
                        print(f"❌ Error processing {entry.link}: {e}")
                        results["errors"] += 1
                        
            except Exception as e:
                print(f"❌ Error fetching feed {feed_url}: {e}")

        return results

    async def process_article(self, entry, source_name):
        url = entry.link
        title = entry.title

        # 2. Check Duplication
        existing = supabase_admin.table("news_articles").select("id").eq("url", url).execute()
        if existing.data:
            raise ValueError("Duplicate article")

        # 3. AI Processing
        full_text = f"{title} - {entry.get('summary', '')}"
        
        # --- התיקון: הוספנו await כאן! ---
        summary = await ai_engine.summarize_article(full_text)
        
        # Embed
        text_to_embed = f"{source_name}: {title}. {summary}"
        vector = ai_engine.get_embedding(text_to_embed)

        article_id = str(uuid.uuid4())

        # 4. Save to Supabase
        article_data = {
            "id": article_id,
            "title": title,
            "url": url,
            "summary": summary,
            "source": source_name,
            "published_at": datetime.now().isoformat()
        }
        supabase_admin.table("news_articles").insert(article_data).execute()

        # 5. Save to Qdrant
        qdrant.upsert(
            collection_name="news_vectors",
            points=[
                PointStruct(
                    id=article_id,
                    vector=vector,
                    payload={
                        "title": title,
                        "url": url,
                        "source": source_name,
                        "summary": summary,
                        "category": "General"
                    }
                )
            ]
        )
        print(f"✅ Saved: {title[:30]}...")

# Export instance
ingestion_service = IngestionService()