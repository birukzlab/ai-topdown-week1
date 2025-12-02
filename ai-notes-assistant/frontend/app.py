import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/analyze-notes"


st.set_page_config(page_title="AI Notes Assistant", page_icon="📝")
st.title("📝 AI Notes Assistant")

st.write(
    "Paste your meeting / lecture / brainstorming notes below, "
    "and I'll summarize them and extract action items."
)

text = st.text_area(
    "Your notes",
    height=250,
    placeholder="Example:\nMeeting with marketing team...\n- Todo: send follow-up email\n- Action: update campaign budget...",
)

if st.button("Summarize & Extract Tasks"):
    if not text.strip():
        st.warning("Please paste some notes first.")
    else:
        with st.spinner("Analyzing notes..."):
            try:
                resp = requests.post(API_URL, json={"text": text})
            except requests.RequestException as e:
                st.error(f"Could not reach backend API: {e}")
            else:
                if resp.status_code != 200:
                    st.error(f"API error: {resp.status_code} - {resp.text}")
                else:
                    data = resp.json()
                    st.subheader("Summary")
                    st.write(data.get("summary", "(no summary)"))

                    st.subheader("Action Items / TODOs")
                    todos = data.get("todos", [])
                    if todos:
                        for i, todo in enumerate(todos, 1):
                            st.write(f"{i}. {todo}")
                    else:
                        st.write("(No todos found.)")
