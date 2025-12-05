import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/digest"


st.set_page_config(page_title="Personal News Digest Agent", page_icon="📰")
st.title("📰 Personal News Digest Agent")

st.write(
    "Enter topics you're interested in (e.g. 'AI, machine learning, startup') "
    "and I'll fetch relevant tech news (from Hacker News for now) and rank them."
)

topics_input = st.text_input(
    "Topics / keywords (comma-separated)",
    value="AI, machine learning, startup",
    help="I'll look for these keywords in article titles.",
)

max_articles = st.slider("Max articles to show", min_value=3, max_value=20, value=8)

if st.button("Generate Digest"):
    topics = [t.strip() for t in topics_input.split(",") if t.strip()]
    if not topics:
        st.warning("Please enter at least one topic.")
    else:
        with st.spinner("Fetching and ranking news..."):
            try:
                resp = requests.post(API_URL, json={"topics": topics, "max_articles": max_articles})
            except requests.RequestException as e:
                st.error(f"Could not reach backend API: {e}")
            else:
                if resp.status_code != 200:
                    st.error(f"API error: {resp.status_code} - {resp.text}")
                else:
                    data = resp.json()
                    articles = data.get("articles", [])
                    if not articles:
                        st.info("No relevant articles found. Try different topics or increase max articles.")
                    else:
                        st.subheader("Your Personalized Digest")
                        st.caption(f"Topics: {', '.join(data.get('topics', []))}")

                        for a in articles:
                            st.markdown(f"### [{a['title']}]({a['url']})")
                            st.caption(f"Source: {a['source']} | Score: {a['score']:.2f}")
                            if a.get("summary"):
                                st.write(a["summary"])
                            st.markdown("---")
