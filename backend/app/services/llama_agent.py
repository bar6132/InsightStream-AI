"""
Llama Agent — Autonomous Topic Selection + Web Search
Uses local Ollama (llama2) as the brain:
  1. Llama decides what topics are hot/important right now
  2. Llama generates a search query for each topic
  3. DuckDuckGo searches the web
  4. newspaper3k scrapes full article text
  5. Returns articles ready for the ingestion pipeline
"""

import asyncio
import json
import re
import time
import random
from typing import Optional
from datetime import datetime

from ddgs import DDGS
from newspaper import Article as NewspaperArticle

from .ollama_fallback import ollama_fallback

# How many topics Llama picks per run
TOPICS_PER_RUN = 3

# Max DDG results per topic
RESULTS_PER_TOPIC = 3


class LlamaAgent:

    async def _call_ollama(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """Send a reasoning prompt to mistral:7b via ollama_fallback."""
        return await ollama_fallback.reason(prompt, temperature=temperature)

    async def pick_hot_topics(self) -> list[str]:
        """
        Ask Llama2 to autonomously decide what topics are important/hot right now.
        Returns a list of topic strings to search for.
        """
        today = datetime.now().strftime("%B %Y")

        prompt = f"""You are an expert news editor in {today}. Your job is to identify the most important and trending news topics RIGHT NOW across tech, AI, Israel, cybersecurity, and global finance.

Generate exactly {TOPICS_PER_RUN} hot topics to search for today. Pick what you think is most newsworthy and interesting.

Rules:
- Output ONLY a JSON array of {TOPICS_PER_RUN} short topic strings, nothing else
- Each topic should be specific, not generic
- Mix different domains (tech, Israel, finance, science, AI, geopolitics)
- Example output: ["OpenAI GPT-5 release", "Israel-Gaza ceasefire talks", "Fed interest rate decision"]

Output:"""

        raw = await self._call_ollama(prompt, temperature=0.8)
        if raw:
            match = re.search(r'\[.*?\]', raw, re.DOTALL)
            if match:
                try:
                    topics = json.loads(match.group())
                    if isinstance(topics, list) and topics:
                        print(f"🧠 [AGENT] Llama chose topics: {topics}")
                        return topics[:TOPICS_PER_RUN]
                except json.JSONDecodeError:
                    pass

        # Fallback topics if Llama fails
        print("⚠️ [AGENT] Llama topic selection failed, using fallback topics")
        return [
            "AI news latest 2026",
            "Israel tech startups 2026",
            "global markets economy today",
        ]

    async def generate_search_query(self, topic: str) -> str:
        """Ask Llama to turn a topic into an optimized search query."""
        prompt = f"""Convert this news topic into a single focused web search query. Output ONLY the query string, nothing else.

Topic: {topic}

Rules:
- Keep it under 8 words
- Add "2026" or "latest" if relevant
- No quotes, no punctuation

Query:"""

        raw = await self._call_ollama(prompt, temperature=0.2, timeout=20.0)
        if raw:
            # Clean up any extra text, take first line only
            query = raw.split('\n')[0].strip().strip('"').strip("'")
            if query:
                print(f"🧠 [AGENT] Search query for '{topic}': '{query}'")
                return query

        return topic

    def search_web(self, query: str) -> list[dict]:
        """Search DuckDuckGo news with rate-limit protection."""
        time.sleep(random.uniform(4, 8))
        try:
            results = list(DDGS().news(query, max_results=RESULTS_PER_TOPIC))
            print(f"🔍 [AGENT] DDG found {len(results)} results for: '{query}'")
            return results
        except Exception as e:
            print(f"❌ [AGENT] DDG search failed for '{query}': {e}")
            return []

    def scrape_article(self, url: str) -> Optional[str]:
        """Scrape full article text. Returns None if scraping fails."""
        try:
            article = NewspaperArticle(url)
            article.download()
            article.parse()
            text = article.text.strip()
            return text if len(text) > 150 else None
        except Exception:
            return None

    async def run(self) -> list[dict]:
        """
        Full agent run:
        1. Llama picks hot topics autonomously
        2. Llama generates search queries for each
        3. DDG searches the web
        4. Scrape + collect articles
        """
        print("🤖 [AGENT] Llama agent starting — picking hot topics...")
        discovered = []
        seen_urls = set()

        # Step 1: Llama picks the topics
        topics = await self.pick_hot_topics()

        for topic in topics:
            print(f"🔎 [AGENT] Topic: '{topic}'")

            # Step 2: Llama generates the search query
            query = await self.generate_search_query(topic)

            # Step 3: Search the web
            results = await asyncio.get_event_loop().run_in_executor(
                None, self.search_web, query
            )

            for result in results:
                url = result.get("url", "")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                title = result.get("title", "")
                source = result.get("source", "Web")
                snippet = result.get("body", "")

                # Step 4: Scrape full text, fall back to snippet
                full_text = await asyncio.get_event_loop().run_in_executor(
                    None, self.scrape_article, url
                )
                text = full_text or snippet
                if not text:
                    continue

                discovered.append({
                    "title": title,
                    "url": url,
                    "source": f"Agent:{source}",
                    "text": text,
                    "published_at": datetime.now().isoformat(),
                })
                print(f"📄 [AGENT] Found: {title[:70]}...")

        print(f"🤖 [AGENT] Done — {len(discovered)} articles discovered")
        return discovered


# Singleton
llama_agent = LlamaAgent()
