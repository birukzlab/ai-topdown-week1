# api_data_fetcher/app.py
import streamlit as st
from fetcher import (
    fetch_bitcoin_price,
    fetch_posts,
    APIError,
)

st.set_page_config(page_title="API Data Fetcher", page_icon="🌐")

st.title("🌐 API Data Fetcher Dashboard")

st.markdown("Small dashboard to practice calling external APIs: "
            "**Bitcoin price** + **Fake posts list**.")


# ----------- Bitcoin Price Section ----------- #
st.header("₿ Bitcoin Price")

col1, col2 = st.columns(2)

with col1:
    currency = st.text_input("Currency code (e.g. USD, EUR, GBP)", "USD")

with col2:
    if st.button("Get BTC price"):
        try:
            price = fetch_bitcoin_price(currency)
            st.success(f"1 BTC ≈ {price:.2f} {currency.upper()}")
        except APIError as e:
            st.error(f"Error: {e}")


st.markdown("---")

# ----------- Posts Section ----------- #
st.header("📝 Posts Browser")

limit = st.slider("How many posts to fetch?", min_value=1, max_value=20, value=5)

if st.button("Fetch posts"):
    try:
        posts = fetch_posts(limit=limit)
        if not posts:
            st.info("No posts returned.")
        else:
            for p in posts:
                with st.expander(f"[{p['id']}] {p['title']}"):
                    st.write(p["body"])
    except APIError as e:
        st.error(f"Error: {e}")

