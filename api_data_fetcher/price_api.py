from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fetcher import fetch_bitcoin_price, APIError

app = FastAPI(
    title="BTC Price API",
    description="Simple API wrapper around CoinGecko to fetch Bitcoin price.",
    version="0.1.0",
)


class PriceOut(BaseModel):
    currency: str
    price: float


@app.get("/btc-price", response_model=PriceOut)
def get_btc_price(currency: str = "USD"):
    """
    Get the current Bitcoin price in the given currency.

    Example:
    /btc-price?currency=USD
    """
    try:
        price = fetch_bitcoin_price(currency)
        return PriceOut(currency=currency.upper(), price=price)
    except APIError as e:
        # 502 Bad Gateway = upstream service failure (CoinGecko)
        raise HTTPException(status_code=502, detail=str(e))
