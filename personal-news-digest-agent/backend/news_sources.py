import requests
from typing import List, Dict, Any

HN_TOPSTORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_URL = "https://hacker-news.firebaseio.com/v0/item/{id}.json"


class NewsSourceError(Exception):
    pass


def fetch_hn_top_stories(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch top stories from Hacker News (up to 'limit').
    Returns a list of dicts with keys: id, title, url, score, source.
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

    articles = []
    for story_id in ids[:limit]:
        try:
            item_resp = requests.get(HN_ITEM_URL.format(id=story_id), timeout=5)
            item_resp.raise_for_status()
            item = item_resp.json()
        except requests.RequestException:
            continue 
        except ValueError:
            continue

        if not item or item.get("type") != "story":
            continue

        title = item.get("title") or "(no title)"
        url = item.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
        score = float(item.get("score") or 0)

        articles.append(
            {
                "id": str(story_id),
                "title": title,
                "url": url,
                "score": score,
                "source": "hackernews",
            }
        )

    return articles
