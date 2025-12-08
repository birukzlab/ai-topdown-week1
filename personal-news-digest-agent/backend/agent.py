# backend/agent.py

"""
Agent logic for building a personalized news digest:

1. Fetch articles from multiple sources (Hacker News + RSS).
2. Optionally filter by source.
3. Compute simple topic relevance scores.
4. Combine relevance with source score.
5. Generate AI summaries for top articles using Gemini.
"""

from typing import List, Dict, Any, Optional

from news_sources import fetch_all_sources
from ai_client import summarize_article


def compute_topic_score(title: str, topics: List[str]) -> float:
    """
    Simple relevance score:
    - Count how many topic keywords appear (case-insensitive) in the title.
    """
    title_lower = title.lower()
    score = 0.0
    for t in topics:
        t_clean = t.strip().lower()
        if not t_clean:
            continue
        if t_clean in title_lower:
            score += 1.0
    return score


def build_digest(
    topics: List[str],
    max_articles: int = 10,
    allowed_sources: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Main agent pipeline.

    Steps:
    1. Fetch lots of articles from all configured sources.
    2. Optionally keep only articles from allowed_sources.
    3. Compute a combined_score = topic_score * 10 + source_score.
    4. Sort and take top max_articles.
    5. Generate summaries using Gemini (or fallback).
    """
    # 1. Fetch from all sources
    raw_articles = fetch_all_sources(limit_per_source=30)

    # 2. Filter by allowed_sources if provided
    if allowed_sources:
        allowed_set = set(allowed_sources)
        raw_articles = [a for a in raw_articles if a["source"] in allowed_set]

    # 3. Score articles
    scored: List[Dict[str, Any]] = []
    for a in raw_articles:
        topic_score = compute_topic_score(a["title"], topics)
        combined_score = topic_score * 10.0 + float(a.get("score", 0.0))

        scored.append(
            {
                **a,
                "relevance_score": topic_score,
                "combined_score": combined_score,
            }
        )

    # 4. Keep only articles with some relevance
    scored = [a for a in scored if a["relevance_score"] > 0.0]

    # 5. Sort by combined_score descending
    scored.sort(key=lambda x: x["combined_score"], reverse=True)

       # 6. Take top N
    top = scored[:max_articles]

    # 7. Generate summaries
    #    To keep latency reasonable, only send the first few articles to Gemini.
    MAX_LLM_SUMMARIES = 2  # you can tune this

    digest_articles: List[Dict[str, Any]] = []
    for idx, a in enumerate(top):
        if idx < MAX_LLM_SUMMARIES:
            # Full AI summary for the top few
            summary_text = summarize_article(
                title=a["title"],
                description=a.get("description"),
                topics=topics,
                url=a.get("url"),
            )
        else:
            # Cheap fallback for the rest (no Gemini call)
            desc = a.get("description") or a["title"]
            summary_text = desc.strip()
            if len(summary_text) > 220:
                summary_text = summary_text[:220] + "..."
            summary_text += "\n\n(Note: This is a simple snippet, not an AI-generated summary.)"

        digest_articles.append(
            {
                "id": a["id"],
                "title": a["title"],
                "url": a["url"],
                "score": a["combined_score"],
                "source": a["source"],
                "summary": summary_text,
            }
        )

    return digest_articles




