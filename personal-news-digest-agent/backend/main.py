from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from typing import List
from schemas import DigestRequest, DigestResponse, ArticleSummary
from agent import build_digest


app = FastAPI(
    title="Personal News Digest Agent",
    description="Fetches recent news and creates a personalized digest based on topics.",
    version="0.1.0",
)

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
    topics = [t.strip() for t in payload.topics if t.strip()]
    if not topics:
        raise HTTPException(status_code=400, detail="At least one non-empty topic is required.")

    try:
        digest_articles = build_digest(topics, max_articles=payload.max_articles)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to build digest: {e}")

    articles = [ArticleSummary(**a) for a in digest_articles]
    return DigestResponse(topics=topics, articles=articles)
