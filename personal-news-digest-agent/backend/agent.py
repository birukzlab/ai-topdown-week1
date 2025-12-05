from typing import List, Dict, Any
from news_sources import fetch_hn_top_stories


def compute_topic_score(title: str, topics: List[str]) -> float:
    """
    Simple relevance score: count of topic keyword matches in the title (case-insensitive).
    """
    title_lower = title.lower()
    score = 0
    for t in topics:
        t_clean = t.strip().lower()
        if not t_clean:
            continue
        if t_clean in title_lower:
            score += 1
    return float(score)


def build_digest(topics: List[str], max_articles: int = 10) -> List[Dict[str, Any]]:
    """
    Agent pipeline:
      1. Fetch top stories from HN
      2. Compute relevance score for each based on topics
      3. Combine relevance score with HN score
      4. Sort and return top 'max_articles'
    """
    raw_articles = fetch_hn_top_stories(limit=100)  # fetch more, then filter down

    scored = []
    for a in raw_articles:
        topic_score = compute_topic_score(a["title"], topics)
        combined_score = topic_score * 10 + a["score"]  # simple heuristic
        scored.append(
            {
                **a,
                "relevance_score": topic_score,
                "combined_score": combined_score,
            }
        )

    # Keep only articles with some relevance
    scored = [a for a in scored if a["relevance_score"] > 0]

    # Sort by combined_score desc
    scored.sort(key=lambda x: x["combined_score"], reverse=True)

    # Take top N
    top = scored[:max_articles]

    # Map to clean structure
    digest_articles = [
        {
            "id": a["id"],
            "title": a["title"],
            "url": a["url"],
            "score": a["combined_score"],
            "source": a["source"],
            "summary": None,  # placeholder for future LLM summary
        }
        for a in top
    ]

    return digest_articles
