from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base
class MarketPrice(Base):
    __tablename__ = "market_prices"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price_usd = Column(Float)
    change_24h = Column(Float)
    volume_24h = Column(Float)
    market_cap = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    source = Column(String)
    url = Column(String, unique=True)
    sentiment = Column(String)
    sentiment_score = Column(Float)
    published_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)