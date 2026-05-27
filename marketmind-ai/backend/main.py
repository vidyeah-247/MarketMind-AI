from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import feedparser

from apscheduler.schedulers.background import BackgroundScheduler
from transformers import pipeline

from database import engine, SessionLocal, Base
from models import MarketPrice, NewsArticle


app = FastAPI(title="MarketMind AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


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


sentiment_model = pipeline(
    "sentiment-analysis",
    model="ProsusAI/finbert",
)

summary_model = pipeline(
    "text-generation",
    model="google/flan-t5-base",
)


@app.get("/")
def home():
    return {"message": "MarketMind AI Backend is running"}


def fetch_and_store_prices():
    db = SessionLocal()

    try:
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
        print("Market prices stored successfully")

    except Exception as e:
        db.rollback()
        print("Error storing market prices:", e)

    finally:
        db.close()


@app.get("/prices")
def get_prices():
    db = SessionLocal()

    try:
        result = []

        for symbol in COINS.keys():
            item = (
                db.query(MarketPrice)
                .filter(MarketPrice.symbol == symbol)
                .order_by(MarketPrice.timestamp.desc())
                .first()
            )

            if item:
                result.append({
                    "symbol": item.symbol,
                    "price_usd": item.price_usd,
                    "change_24h": item.change_24h,
                    "volume_24h": item.volume_24h,
                    "market_cap": item.market_cap,
                    "timestamp": item.timestamp,
                })

        return result

    finally:
        db.close()


@app.get("/history/{symbol}")
def get_price_history(symbol: str):
    db = SessionLocal()

    try:
        prices = (
            db.query(MarketPrice)
            .filter(MarketPrice.symbol == symbol.upper())
            .order_by(MarketPrice.timestamp.desc())
            .limit(100)
            .all()
        )

        result = []

        for item in reversed(prices):
            result.append({
                "symbol": item.symbol,
                "price_usd": item.price_usd,
                "change_24h": item.change_24h,
                "volume_24h": item.volume_24h,
                "market_cap": item.market_cap,
                "timestamp": item.timestamp,
            })

        return result

    finally:
        db.close()


def analyze_sentiment(title: str):
    try:
        result = sentiment_model(title)[0]

        label = result["label"].lower()
        score = float(result["score"])

        return label, score

    except Exception as e:
        print("Sentiment error:", e)
        return "neutral", 0.0


def fetch_and_store_news():
    db = SessionLocal()

    try:
        feed_url = "https://cointelegraph.com/rss"
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:20]:
            title = entry.title
            url = entry.link

            existing = db.query(NewsArticle).filter(NewsArticle.url == url).first()

            if existing:
                continue

            sentiment, score = analyze_sentiment(title)

            article = NewsArticle(
                title=title,
                source="Cointelegraph",
                url=url,
                sentiment=sentiment,
                sentiment_score=score,
            )

            db.add(article)

        db.commit()
        print("News articles stored successfully")

    except Exception as e:
        db.rollback()
        print("Error storing news:", e)

    finally:
        db.close()


@app.get("/news")
def get_news():
    db = SessionLocal()

    try:
        articles = (
            db.query(NewsArticle)
            .order_by(NewsArticle.created_at.desc())
            .limit(20)
            .all()
        )

        result = []

        for article in articles:
            result.append({
                "title": article.title,
                "source": article.source,
                "url": article.url,
                "sentiment": article.sentiment,
                "sentiment_score": article.sentiment_score,
                "published_at": article.published_at,
                "created_at": article.created_at,
            })

        return result

    finally:
        db.close()


@app.get("/summary")
def get_market_summary():
    db = SessionLocal()

    try:
        articles = (
            db.query(NewsArticle)
            .order_by(NewsArticle.created_at.desc())
            .limit(10)
            .all()
        )

        if not articles:
            return {
                "overall_sentiment": "Neutral",
                "summary": "No news articles available.",
                "positive_news": 0,
                "negative_news": 0,
                "neutral_news": 0,
                "total_articles": 0,
            }

        positive = sum(1 for a in articles if a.sentiment == "positive")
        negative = sum(1 for a in articles if a.sentiment == "negative")
        neutral = sum(1 for a in articles if a.sentiment == "neutral")

        if positive > negative:
            overall = "Bullish"
        elif negative > positive:
            overall = "Bearish"
        else:
            overall = "Neutral"

        headlines = "\n".join([f"- {article.title}" for article in articles])

        prompt = (
            "Summarize these crypto news headlines in 2 short sentences. "
            "Do not repeat the headlines. Focus on overall market mood.\n\n"
            f"{headlines}\n\n"
            "Summary:"
        )

        summary_result = summary_model(
            prompt,
            max_new_tokens=100,
            do_sample=False,
        )

        generated = summary_result[0].get("generated_text", "").strip()

        ai_summary = generated.replace(prompt, "").strip()

        if "Summary:" in ai_summary:
            ai_summary = ai_summary.split("Summary:")[-1].strip()

        if not ai_summary:
            ai_summary = (
                f"The crypto market currently appears {overall.lower()} "
                f"with {negative} negative, {positive} positive, and "
                f"{neutral} neutral headlines dominating recent news."
            )

        return {
            "overall_sentiment": overall,
            "summary": ai_summary,
            "positive_news": positive,
            "negative_news": negative,
            "neutral_news": neutral,
            "total_articles": len(articles),
        }

    except Exception as e:
        print("Summary error:", e)
        return {
            "overall_sentiment": "Neutral",
            "summary": "AI summary could not be generated right now.",
            "positive_news": 0,
            "negative_news": 0,
            "neutral_news": 0,
            "total_articles": 0,
        }

    finally:
        db.close()


fetch_and_store_prices()
fetch_and_store_news()

scheduler = BackgroundScheduler()

scheduler.add_job(fetch_and_store_prices, "interval", seconds=30)
scheduler.add_job(fetch_and_store_news, "interval", minutes=5)

scheduler.start()
