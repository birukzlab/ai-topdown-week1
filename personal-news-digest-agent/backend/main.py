# backend/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import List

from schemas import DigestRequest, DigestResponse, ArticleSummary
from agent import build_digest
from ai_client import get_usage_stats

app = FastAPI(
    title="Personal News Digest Agent",
    description="Fetches recent news from multiple sources and creates a personalized digest with AI summaries.",
    version="0.2.0",
)

# Allow Streamlit on localhost to call this API
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/digest", response_model=DigestResponse)
def create_digest(payload: DigestRequest):
    """
    Main endpoint: build a personalized digest for the given topics.
    """
    topics = [t.strip() for t in payload.topics if t.strip()]
    if not topics:
        raise HTTPException(status_code=400, detail="At least one non-empty topic is required.")

    allowed_sources = payload.sources  # may be None

    try:
        digest_articles = build_digest(
            topics=topics,
            max_articles=payload.max_articles,
            allowed_sources=allowed_sources,
        )
    except Exception as e:
        # Catch-all for upstream/source errors
        raise HTTPException(status_code=502, detail=f"Failed to build digest: {e}")

    articles = [ArticleSummary(**a) for a in digest_articles]
    return DigestResponse(topics=topics, articles=articles)

@app.get("/usage")
def usage():
    """
    Return aggregate Gemini usage stats (calls, tokens, estimated cost).
    """
    return get_usage_stats()   # 👈 returns dict from ai_client


