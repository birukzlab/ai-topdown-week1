# backend/ai_client.py

"""
Gemini 2.5 Flash integration for article summarization + JSON cache + usage tracking.

- Reads API key from GEMINI_API_KEY or GOOGLE_API_KEY.
- summarize_article() will:
  * Check JSON file cache by URL
  * If cached, return stored summary (no API call)
  * Otherwise call Gemini, track tokens, store in cache
  * On failures or missing key, fall back to a simple snippet

- get_usage_stats() exposes total calls, tokens, and estimated cost.
"""

import os
import time
from threading import Lock
from typing import Optional, List, Dict, Any

import google.generativeai as genai

from cache import get_cached_summary, save_cached_summary

# --------- API KEY + MODEL CONFIG --------- #

# Accept either GEMINI_API_KEY or GOOGLE_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    print("[INFO] Gemini API key loaded successfully.")
else:
    print(
        "[INFO] No Gemini API key found (GEMINI_API_KEY / GOOGLE_API_KEY). "
        "Falling back to non-AI summaries."
    )

# Use Gemini 2.5 Flash (text model)
GEMINI_MODEL_NAME = "gemini-2.5-flash"

# Approximate pricing (per 1M tokens) — override via env if you want
# Input:  $0.30 / 1M tokens
# Output: $2.50 / 1M tokens
COST_INPUT_PER_M = float(os.getenv("GEMINI_COST_INPUT_PER_M", "0.30"))
COST_OUTPUT_PER_M = float(os.getenv("GEMINI_COST_OUTPUT_PER_M", "2.50"))

# --------- USAGE TRACKING (IN-MEMORY) --------- #

_USAGE_LOCK = Lock()
_USAGE_STATS: Dict[str, Any] = {
    "calls": 0,
    "prompt_tokens": 0,
    "response_tokens": 0,
}


def _record_usage(prompt_tokens: int, response_tokens: int) -> None:
    with _USAGE_LOCK:
        _USAGE_STATS["calls"] += 1
        _USAGE_STATS["prompt_tokens"] += int(prompt_tokens)
        _USAGE_STATS["response_tokens"] += int(response_tokens)


def get_usage_stats() -> Dict[str, Any]:
    """
    Return a dict with:
      - calls
      - prompt_tokens
      - response_tokens
      - estimated_input_cost_usd
      - estimated_output_cost_usd
      - estimated_total_cost_usd
    """
    with _USAGE_LOCK:
        stats = dict(_USAGE_STATS)  # shallow copy

    input_cost = stats["prompt_tokens"] / 1_000_000 * COST_INPUT_PER_M
    output_cost = stats["response_tokens"] / 1_000_000 * COST_OUTPUT_PER_M
    total_cost = input_cost + output_cost

    stats["estimated_input_cost_usd"] = round(input_cost, 6)
    stats["estimated_output_cost_usd"] = round(output_cost, 6)
    stats["estimated_total_cost_usd"] = round(total_cost, 6)

    return stats


# --------- PROMPT + SUMMARY LOGIC --------- #


def _build_summary_prompt(
    title: str,
    description: Optional[str],
    topics: List[str],
    url: Optional[str] = None,
) -> str:
    """
    Build a concise prompt for the LLM using title + snippet + topics.
    """
    topics_str = ", ".join(topics) if topics else "the user's interests"
    desc_text = description or "(No description provided.)"
    url_part = f"\nURL: {url}" if url else ""

    prompt = f"""
You are a concise news assistant.

User interests: {topics_str}

Title: {title}
Snippet: {desc_text}{url_part}

Task:
- Write a clear, neutral, 2–3 sentence summary of what this article is about.
- Focus on the main idea and why it might matter to someone interested in the topics above.
- Do NOT use bullet points.
- Do NOT include headers, markdown, or emojis.
- Just return the plain-text summary.
""".strip()

    return prompt


def summarize_article(
    title: str,
    description: Optional[str],
    topics: List[str],
    url: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: float = 1.5,
) -> str:
    """
    Summarize an article using Gemini 2.5 Flash, with:
      - JSON cache by URL
      - usage tracking
      - fallback on failure / missing key
    """
    # 1) Check cache first
    cached = get_cached_summary(url)
    if cached:
        return cached

    # 2) If no API key, skip Gemini and fallback
    if not GEMINI_API_KEY:
        return _fallback_summary(title, description, topics)

    prompt = _build_summary_prompt(title, description, topics, url)

    last_error: Optional[Exception] = None

    for attempt in range(1, max_retries + 1):
        try:
            model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            response = model.generate_content(prompt)

            summary_text = (response.text or "").strip()
            if not summary_text:
                print("[WARN] Gemini returned empty summary; using fallback.")
                return _fallback_summary(title, description, topics)

            # Extract token usage (if available)
            usage = getattr(response, "usage_metadata", None)
            prompt_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
            response_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0

            _record_usage(prompt_tokens, response_tokens)
            save_cached_summary(
                url=url,
                title=title,
                description=description,
                summary=summary_text,
                model=GEMINI_MODEL_NAME,
                prompt_tokens=prompt_tokens,
                response_tokens=response_tokens,
            )

            return summary_text

        except Exception as e:
            last_error = e
            print(f"[WARN] Gemini summarization failed (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(retry_delay)
            else:
                break

    print(f"[ERROR] All Gemini attempts failed. Last error: {last_error}")
    return _fallback_summary(title, description, topics)


def _fallback_summary(
    title: str,
    description: Optional[str],
    topics: List[str],
) -> str:
    """
    Fallback when LLM is unavailable or fails.
    Uses the description or title and labels it as non-AI snippet.
    """
    base = (description or title).strip()
    if len(base) > 220:
        base = base[:220] + "..."

    topics_str = ", ".join(topics) if topics else "your interests"

    return f"{base}\n\n(Note: This is a simple snippet based on the feed, not an AI-generated summary. Topics: {topics_str})"
