# api_data_fetcher/app.py
import streamlit as st
from fetcher import fetch_bitcoin_price, fetch_posts, APIError

st.title("API Data Fetcher")

st.header("Bitcoin Price")
currency = st.text_input("Currency (e.g. USD, EUR, GBP)", "USD")

if st.button("Get BTC price"):
    try:
        price = fetch_bitcoin_price(currency)
        st.success(f"1 BTC ≈ {price:.2f} {currency.upper()}")
    except APIError as e:
        st.error(str(e))

st.header("Posts")
limit = st.number_input("Number of posts to fetch", min_value=1, max_value=100, value=5)

if st.button("Fetch posts"):
    try:
        posts = fetch_posts(limit=limit)
        for p in posts:
            st.write(f"**[{p['id']}] {p['title']}**")
            st.caption(p["body"])
    except APIError as e:
        st.error(str(e))
