# backend/news_sources.py

import requests
import feedparser
from typing import List, Dict, Any

HN_TOPSTORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


class NewsSourceError(Exception):
    """
    Custom exception for news source failures.
    """
    pass


# ---------- Hacker News ---------- #


def fetch_hn_top_stories(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch top stories from Hacker News (up to 'limit').
    Returns a list of dicts with keys:
        id, title, url, score, source, description
    """
    try:
        resp = requests.get(HN_TOPSTORIES_URL, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise NewsSourceError(f"Failed to fetch top story IDs: {e}")

    try:
        ids = resp.json()
    except ValueError as e:
        raise NewsSourceError(f"Invalid JSON from HN: {e}")

    articles: List[Dict[str, Any]] = []
    for story_id in ids[:limit]:
        try:
            item_resp = requests.get(HN_ITEM_URL.format(id=story_id), timeout=5)
            item_resp.raise_for_status()
            item = item_resp.json()
        except (requests.RequestException, ValueError):
            continue

        if not item or item.get("type") != "story":
            continue

        title = item.get("title") or "(no title)"
        url = item.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
        score = float(item.get("score") or 0)

        articles.append(
            {
                "id": f"hn-{story_id}",
                "title": title,
                "url": url,
                "score": score,
                "source": "hackernews",
                "description": None,  # HN doesn't provide summary
            }
        )

    return articles


# ---------- Generic RSS Fetcher ---------- #


def fetch_rss_feed(url: str, source_name: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch articles from an RSS/Atom feed and normalize them.
    Returns list of dicts with keys:
        id, title, url, score, source, description
    """
    feed = feedparser.parse(url)
    articles: List[Dict[str, Any]] = []

    for entry in feed.entries[:limit]:
        title = getattr(entry, "title", "(no title)")
        link = getattr(entry, "link", None)
        if not link:
            # skip entries without URL
            continue

        desc = getattr(entry, "summary", None) or getattr(entry, "description", None)

        articles.append(
            {
                "id": f"{source_name}-{getattr(entry, 'id', link)}",
                "title": title,
                "url": link,
                "score": 0.0,  # RSS feeds don't have a native score
                "source": source_name,
                "description": desc,
            }
        )

    return articles


# ---------- Multi-source Aggregator ---------- #

# You can customize these with any free tech/news RSS feeds
RSS_FEEDS = [
    ("https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml", "nytimes-tech"),
    ("https://www.theverge.com/rss/index.xml", "theverge"),
    ("https://feeds.bbci.co.uk/news/technology/rss.xml", "bbc-tech"),
    ("https://feeds.arstechnica.com/arstechnica/index", "ars-technica"),
    ("https://www.wired.com/feed/rss", "wired"),
]


def fetch_all_sources(limit_per_source: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch articles from multiple sources (Hacker News + RSS feeds)
    and return a combined, deduplicated list.
    """
    all_articles: List[Dict[str, Any]] = []

    # 1. Hacker News
    try:
        hn_articles = fetch_hn_top_stories(limit=limit_per_source)
        all_articles.extend(hn_articles)
    except NewsSourceError as e:
        print(f"[WARN] Hacker News source failed: {e}")

    # 2. RSS feeds
    for feed_url, source_name in RSS_FEEDS:
        try:
            rss_articles = fetch_rss_feed(feed_url, source_name, limit=limit_per_source)
            all_articles.extend(rss_articles)
        except Exception as e:
            print(f"[WARN] RSS source '{source_name}' failed: {e}")

    # Deduplicate by URL
    deduped: Dict[str, Dict[str, Any]] = {}
    for a in all_articles:
        url = a["url"]
        if url not in deduped:
            deduped[url] = a

    return list(deduped.values())

