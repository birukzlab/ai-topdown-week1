from typing import List
import textwrap


def simple_fallback_summary(text: str, max_chars: int = 200) -> str:
    """
    Naive 'summary' that just truncates the text.
    Later, replace this with a real LLM call.
    """
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def simple_fallback_todos(text: str) -> List[str]:
    """
    Very naive todo extractor:
    - splits by lines
    - keeps lines that start with '-', '*', or contain 'todo'/'action'
    """
    todos: List[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if not stripped:
            continue
        if stripped.startswith(("-", "*")) or "todo" in lower or "action" in lower:
            todos.append(stripped.lstrip("-* ").strip())
    return todos or ["(No clear TODOs found. Add bullet points like '- call client'.)"]


def analyze_notes_with_ai(text: str) -> dict:
    """
    Main AI entrypoint.
    For now uses fallback logic.
    Later you can replace the summary/todo logic
    with an actual LLM call.
    """
    summary = simple_fallback_summary(text)
    todos = simple_fallback_todos(text)
    return {"summary": summary, "todos": todos}

