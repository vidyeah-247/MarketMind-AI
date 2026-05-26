from database import engine, SessionLocal, Base
from models import MarketPrice
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
app = FastAPI(title="MarketMind AI Backend")
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "DOGE": "dogecoin",
    "ADA": "cardano",
    "AVAX": "avalanche-2",
    "DOT": "polkadot",
    "MATIC": "matic-network",
}
@app.get("/")
def home():
    return {"message": "MarketMind AI Backend is running"}
@app.get("/prices")
@app.get("/prices")
def get_prices():
    db = SessionLocal()
    coin_ids = ",".join(COINS.values())
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": coin_ids,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_24hr_vol": "true",
        "include_market_cap": "true",
    }
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    result = []
    for symbol, coin_id in COINS.items():
        coin_data = data.get(coin_id, {})
        market_entry = MarketPrice(
            symbol=symbol,
            price_usd=coin_data.get("usd"),
            change_24h=coin_data.get("usd_24h_change", 0),
            volume_24h=coin_data.get("usd_24h_vol", 0),
            market_cap=coin_data.get("usd_market_cap", 0),
        )
        db.add(market_entry)
        result.append({
            "symbol": symbol,
            "price_usd": coin_data.get("usd"),
            "change_24h": round(coin_data.get("usd_24h_change", 0), 2),
            "volume_24h": round(coin_data.get("usd_24h_vol", 0), 2),
            "market_cap": round(coin_data.get("usd_market_cap", 0), 2),
        })
    db.commit()
    db.close()
    return result