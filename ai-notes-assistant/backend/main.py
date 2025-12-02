from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import NotesIn, NotesAnalysisOut
from ai_client import analyze_notes_with_ai


app = FastAPI(
    title="AI Notes Assistant API",
    description="Summarize notes and extract action items.",
    version="0.1.0",
)

# Allow Streamlit (usually running on http://localhost:8501) to call this API
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


@app.post("/analyze-notes", response_model=NotesAnalysisOut)
def analyze_notes(payload: NotesIn):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    result = analyze_notes_with_ai(text)
    return NotesAnalysisOut(**result)
