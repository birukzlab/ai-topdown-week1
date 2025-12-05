# Personal News Digest Agent 📰

A project to learn **AI engineering top-down** by building a
small full-stack system:

- **FastAPI** backend (API)
- **Streamlit** frontend (UI)
- **Agent** pipeline that fetches news, scores them by topic, and returns a digest.

## How it works

1. You enter topics like: `AI, machine learning, startup`
2. Backend:
   - Fetches top Hacker News stories
   - Scores each story based on topic matches
   - Sorts and returns the top N as your digest
3. Frontend:
   - Calls the `/digest` API
   - Shows a ranked list of news articles

Later, this can be extended with:
- LLM-based summarization of each article
- Multiple sources (RSS, NewsAPI, etc.)
- Daily scheduled digests

## Tech stack

- Python
- FastAPI (backend)
- Streamlit (frontend)
- requests (HTTP to news sources)

## Run locally

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
