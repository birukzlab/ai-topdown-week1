# frontend/app.py

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/digest"
USAGE_API_URL = "http://127.0.0.1:8000/usage"

# These must match the sources used in backend/news_sources.py
available_sources = [
    "hackernews",
    "nytimes-tech",
    "theverge",
    "bbc-tech",
    "ars-technica",
    "wired",
]


def fetch_usage():
    """
    Call the backend /usage endpoint to get aggregate Gemini usage stats.
    Returns a dict or None if not available.
    """
    try:
        resp = requests.get(USAGE_API_URL, timeout=3)
        if resp.status_code == 200:
            return resp.json()
        return None
    except requests.RequestException:
        return None


# ---------- Streamlit UI ---------- #

st.set_page_config(page_title="Personal News Digest Agent", page_icon="📰")

# Sidebar: API Usage / Cost
with st.sidebar:
    st.header("API Usage")

    usage = fetch_usage()
    if usage is None:
        st.caption("Usage info not available yet.")
    else:
        total_cost = usage.get("estimated_total_cost_usd", 0.0) or 0.0
        prompt_tokens = usage.get("prompt_tokens", 0)
        response_tokens = usage.get("response_tokens", 0)
        calls = usage.get("calls", 0)

        # Main metric: total estimated cost
        st.metric("API Cost", f"${total_cost:.4f}")

        # Extra details
        st.write(f"Calls: {calls}")
        st.write(f"Prompt tokens: {prompt_tokens}")
        st.write(f"Response tokens: {response_tokens}")

        st.caption(
            "Costs are approximate and based on configured per-million-token rates "
            "(GEMINI_COST_INPUT_PER_M, GEMINI_COST_OUTPUT_PER_M). "
            "Counters reset when the backend restarts."
        )

# Main page
st.title("📰 Personal News Digest Agent")

st.write(
    "Enter topics you're interested in (e.g. 'AI, machine learning, startup') "
    "and I'll fetch relevant tech news from multiple sources, rank them, "
    "and summarize each article using Gemini."
)

topics_input = st.text_input(
    "Topics / keywords (comma-separated)",
    value="AI, machine learning, startup",
    help="I'll look for these keywords in article titles.",
)

max_articles = st.slider("Max articles to show", min_value=3, max_value=20, value=8)

selected_sources = st.multiselect(
    "Filter by source (optional)",
    options=available_sources,
    default=available_sources,
    help="Unselect sources you want to exclude. If you keep all selected, all sources are used.",
)

if st.button("Generate Digest"):
    topics = [t.strip() for t in topics_input.split(",") if t.strip()]
    if not topics:
        st.warning("Please enter at least one topic.")
    else:
        payload = {
            "topics": topics,
            "max_articles": max_articles,
        }

        # Only send 'sources' if user deselected some sources
        if 0 < len(selected_sources) < len(available_sources):
            payload["sources"] = selected_sources

        with st.spinner("Fetching, ranking, and summarizing news..."):
            try:
                resp = requests.post(API_URL, json=payload, timeout=60)
            except requests.RequestException as e:
                st.error(f"Could not reach backend API: {e}")
            else:
                if resp.status_code != 200:
                    st.error(f"API error: {resp.status_code} - {resp.text}")
                else:
                    data = resp.json()
                    articles = data.get("articles", [])
                    if not articles:
                        st.info("No relevant articles found. Try different topics or sources.")
                    else:
                        st.subheader("Your Personalized Digest")
                        st.caption(f"Topics: {', '.join(data.get('topics', []))}")

                        for a in articles:
                            st.markdown(f"### [{a['title']}]({a['url']})")
                            st.caption(f"Source: `{a['source']}` | Score: {a['score']:.2f}")

                            summary = a.get("summary")
                            if summary:
                                st.write(summary)
                            else:
                                st.write("_No summary available for this article._")

                            st.markdown("---")

