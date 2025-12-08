# backend/cache.py

"""
File-based JSON cache for article summaries.

- Keyed by URL
- Stores: title, description, summary, model, token usage, created_at
- Thread-safe via a simple lock
"""

import json
from pathlib import Path
from threading import Lock
from datetime import datetime
from typing import Optional, Dict, Any

CACHE_FILE_PATH = Path(__file__).parent / "summary_cache.json"
_CACHE_LOCK = Lock()


def _load_cache() -> Dict[str, Any]:
    """
    Load the entire cache from disk.
    Returns a dict: {url: { ...entry... }, ...}
    """
    with _CACHE_LOCK:
        if not CACHE_FILE_PATH.exists():
            return {}

        try:
            with CACHE_FILE_PATH.open("r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data
            # If file structure is weird, start fresh
            return {}
        except Exception:
            # If file is corrupted or unreadable, start fresh
            return {}


def _save_cache(cache: Dict[str, Any]) -> None:
    """
    Save the entire cache to disk (overwrite).
    """
    with _CACHE_LOCK:
        with CACHE_FILE_PATH.open("w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)


def get_cached_summary(url: Optional[str]) -> Optional[str]:
    """
    Return cached summary for this URL, or None if not found.
    """
    if not url:
        return None

    cache = _load_cache()
    entry = cache.get(url)
    if entry and isinstance(entry, dict):
        return entry.get("summary")
    return None

def save_cached_summary(
    url: Optional[str],
    title: str,
    description: Optional[str],
    summary: str,
    model: str,
    prompt_tokens: int,
    response_tokens: int,
) -> None:
    """
    Save or update a cached summary for this URL.
    """
    if not url:
        # No URL = nothing to key on
        return

    cache = _load_cache()

    cache[url] = {
        "url": url,
        "title": title,
        "description": description,
        "summary": summary,
        "model": model,
        "prompt_tokens": int(prompt_tokens),
        "response_tokens": int(response_tokens),
        "created_at": datetime.utcnow().isoformat(),
    }

    _save_cache(cache)
