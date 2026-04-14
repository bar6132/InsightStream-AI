import feedparser
import uuid
from datetime import datetime
from ..core.database import supabase, supabase_admin, qdrant
from ..services.ai_engine import ai_engine
from ..services.llama_agent import llama_agent
from qdrant_client.models import PointStruct
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_not_exception_type

# --- 1. RSS FEEDS LIST ---
RSS_FEEDS = [
    # --- Tech & AI ---
    "http://feeds.feedburner.com/TechCrunch/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.technologyreview.com/feed/",

    # --- Israel News (English) ---
    "https://www.jpost.com/rss/rssfeedsheadlines.aspx",
    "https://www.timesofisrael.com/feed/",

    # --- Israel News (Hebrew) ---
    "https://www.maariv.co.il/rss/rss-news",
    "https://www.ynet.co.il/Integration/StoryRss1854.xml",
    "https://www.mako.co.il/rss/31750a2610f26110VgnVCM1000005201010aRCRD.xml",

    # --- Economy & Finance ---
    "https://feeds.bloomberg.com/markets/news.rss",

    # --- Science & World ---
    "https://www.sciencedaily.com/rss/all.xml",
    "http://feeds.bbci.co.uk/news/rss.xml",
]

class IngestionService:
    async def run_pipeline(self):
        """
        Main entry point: Fetches, Summarizes, Vectorizes, and Saves.
        Phase 1 — RSS feeds
        Phase 2 — Llama agent web search
        """
        results = {"added": 0, "errors": 0, "skipped": 0}
        print("🚀 Starting Enhanced Ingestion Pipeline...")

        # ── Phase 1: RSS Feeds ──────────────────────────────────────
        print("📡 [Phase 1] RSS feeds...")
        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                source_name = feed.feed.get("title", "Unknown Source")
                print(f"📥 Parsing: {source_name} ({len(feed.entries)} items)")

                for entry in feed.entries[:5]:
                    try:
                        await self.process_article(entry, source_name)
                        results["added"] += 1
                    except ValueError:
                        results["skipped"] += 1
                    except Exception as e:
                        print(f"❌ Error processing {entry.get('link', 'unknown')}: {type(e).__name__}: {e}")
                        results["errors"] += 1

            except Exception as e:
                print(f"❌ Error fetching feed {feed_url}: {e}")

        # ── Phase 2: Llama Agent Web Search ────────────────────────
        print("🤖 [Phase 2] Llama agent web search...")
        try:
            agent_articles = await llama_agent.run()
            for article in agent_articles:
                try:
                    await self.process_agent_article(article)
                    results["added"] += 1
                except ValueError:
                    results["skipped"] += 1
                except Exception as e:
                    print(f"❌ Agent article error ({article.get('url', '?')}): {type(e).__name__}: {e}")
                    results["errors"] += 1
        except Exception as e:
            print(f"❌ Llama agent phase failed: {e}")

        return results

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_not_exception_type(ValueError)
    )
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

    async def process_agent_article(self, article: dict):
        """Process an article discovered by the Llama agent."""
        url = article["url"]
        title = article["title"]
        source_name = article["source"]

        # Duplicate check
        existing = supabase_admin.table("news_articles").select("id").eq("url", url).execute()
        if existing.data:
            raise ValueError("Duplicate article")

        # Summarize
        summary = await ai_engine.summarize_article(article["text"])

        # Embed
        vector = ai_engine.get_embedding(f"{source_name}: {title}. {summary}")

        article_id = str(uuid.uuid4())

        # Save to Supabase
        supabase_admin.table("news_articles").insert({
            "id": article_id,
            "title": title,
            "url": url,
            "summary": summary,
            "source": source_name,
            "published_at": article.get("published_at", datetime.now().isoformat()),
        }).execute()

        # Save to Qdrant
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
                        "category": "Agent"
                    }
                )
            ]
        )
        print(f"✅ [Agent] Saved: {title[:50]}...")


# Export instance
ingestion_service = IngestionService()