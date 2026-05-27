from apscheduler.schedulers.background import BackgroundScheduler
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
def fetch_and_store_prices():
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
    db.commit()
    db.close()
    print("Market prices stored successfully")
@app.get("/prices")
def get_prices():

    db = SessionLocal()

    latest_prices = db.query(MarketPrice)\
        .order_by(MarketPrice.timestamp.desc())\
        .limit(20)\
        .all()

    db.close()

    result = []

    for item in latest_prices:

        result.append({
            "symbol": item.symbol,
            "price_usd": item.price_usd,
            "change_24h": item.change_24h,
            "volume_24h": item.volume_24h,
            "market_cap": item.market_cap,
            "timestamp": item.timestamp
        })

    return result
scheduler = BackgroundScheduler()
scheduler.add_job(
    fetch_and_store_prices,
    'interval',
    seconds=30
)
scheduler.start()
@app.get("/history/{symbol}")
def get_price_history(symbol: str):
    db = SessionLocal()

    prices = db.query(MarketPrice)\
        .filter(MarketPrice.symbol == symbol.upper())\
        .order_by(MarketPrice.timestamp.desc())\
        .limit(100)\
        .all()

    db.close()

    result = []

    for item in reversed(prices):
        result.append({
            "symbol": item.symbol,
            "price_usd": item.price_usd,
            "change_24h": item.change_24h,
            "volume_24h": item.volume_24h,
            "market_cap": item.market_cap,
            "timestamp": item.timestamp
        })

    return result