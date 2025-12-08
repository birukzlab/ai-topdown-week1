from pydantic import BaseModel, Field
from typing import List, Optional


class DigestRequest(BaseModel):
    topics: List[str] = Field(..., description="List of topics/keywords, e.g. ['ai', 'data', 'startups']")
    max_articles: int = Field(10, ge=1, le=50, description="Max number of articles in the digest")
    sources: Optional[List[str]] = Field(
        None,
        description="Optional list of source names to filter by (e.g. ['hackernews', 'bbc-tech']). If omitted, use all sources.",
    )


class ArticleSummary(BaseModel):
    id: str
    title: str
    url: str
    score: float
    source: str
    summary: Optional[str] = None   # For future LLM summaries


class DigestResponse(BaseModel):
    topics: List[str]
    articles: List[ArticleSummary]
