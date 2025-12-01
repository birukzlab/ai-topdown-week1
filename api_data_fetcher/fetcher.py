import requests
from typing import Any, Dict, List, Optional


class APIError(Exception):
    """Custom exception for API-related errors."""
    pass


def fetch_bitcoin_price(currency: str = "USD") -> float:
    """
    Fetch the current Bitcoin price in the given currency using CoinGecko API.

    :param currency: Currency code like 'USD', 'EUR', 'GBP'
    :return: Price of 1 BTC in that currency
    :raises APIError: if the request fails or data is missing
    """
    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": "bitcoin",
        "vs_currencies": currency.lower(),  # API expects lowercase
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
    except requests.RequestException as e:
        raise APIError(f"Network error while calling CoinGecko API: {e}")

    if resp.status_code != 200:
        raise APIError(f"CoinGecko API returned status {resp.status_code}")

    try:
        data = resp.json()
    except ValueError as e:
        raise APIError(f"Invalid JSON from CoinGecko API: {e}")

    # Expected format: {"bitcoin": {"usd": 12345.67}}
    if "bitcoin" not in data:
        raise APIError("Missing 'bitcoin' key in API response")

    key = currency.lower()
    btc_info = data["bitcoin"]

    if key not in btc_info:
        raise APIError(f"Currency {currency} not found in API response")

    return float(btc_info[key])


def fetch_posts(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Fetch a list of posts from JSONPlaceholder.

    :param limit: Optional limit on number of posts to return
    :return: List of posts
    :raises APIError: if the request fails
    """
    url = "https://jsonplaceholder.typicode.com/posts"

    try:
        resp = requests.get(url, timeout=5)
    except requests.RequestException as e:
        raise APIError(f"Network error while calling posts API: {e}")

    if resp.status_code != 200:
        raise APIError(f"Posts API returned status {resp.status_code}")

    try:
        posts = resp.json()
    except ValueError as e:
        raise APIError(f"Invalid JSON from posts API: {e}")

    if not isinstance(posts, list):
        raise APIError("Unexpected posts API response format (expected a list)")

    if limit is not None:
        return posts[:limit]
    return posts


def fetch_post_by_id(post_id: int) -> Dict[str, Any]:
    """
    Fetch a single post by ID.

    :param post_id: ID of the post
    :return: Post dict
    :raises APIError: if not found or request fails
    """
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"

    try:
        resp = requests.get(url, timeout=5)
    except requests.RequestException as e:
        raise APIError(f"Network error while calling posts API: {e}")

    if resp.status_code == 404:
        raise APIError(f"Post with id={post_id} not found")
    if resp.status_code != 200:
        raise APIError(f"Posts API returned status {resp.status_code}")

    try:
        post = resp.json()
    except ValueError as e:
        raise APIError(f"Invalid JSON from posts API: {e}")

    return post
