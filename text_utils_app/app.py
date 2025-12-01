import streamlit as st
from utils import get_stats, transform_text

st.title("Text Utility App")

user_text = st.text_area("Paste your text here")

if st.button("Analyze"):
    stats = get_stats(user_text)
    st.write(f"Characters: {stats['chars']}")
    st.write(f"Words: {stats['words']}")
    st.write(f"Estimated reading time: {stats['reading_time_min']:.2f} min")

st.subheader("Transform Text")

option = st.selectbox(
    "Choose transform",
    ["UPPERCASE", "lowercase", "Title Case"],
)

if st.button("Transform"):
    st.text(transform_text(user_text, option))