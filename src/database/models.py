from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import config

Base = declarative_base()


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    position_id = Column(String, unique=True)
    symbol = Column(String)
    entry_price = Column(Float)
    exit_price = Column(Float)
    units = Column(Float)
    side = Column(String)
    pnl = Column(Float)
    return_pct = Column(Float)
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)
    strategy = Column(String)
    trade_metadata = Column(JSON)


class Signal(Base):
    __tablename__ = 'signals'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    symbol = Column(String)
    signal_type = Column(String)
    strength = Column(Float)
    confidence = Column(Float)
    strategy_name = Column(String)
    acted_upon = Column(Boolean, default=False)
    signal_metadata = Column(JSON)


class MarketData(Base):
    __tablename__ = 'market_data'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    symbol = Column(String)
    exchange = Column(String)
    timeframe = Column(String)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)


class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    position_id = Column(String, unique=True)
    symbol = Column(String)
    entry_price = Column(Float)
    units = Column(Float)
    side = Column(String)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    entry_time = Column(DateTime)
    is_open = Column(Boolean, default=True)
    unrealized_pnl = Column(Float)


class NewsEvent(Base):
    """Store classified news events from Twitter and other sources."""
    __tablename__ = 'news_events'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String)  # 'twitter', 'reddit', etc.
    source_id = Column(String)  # Tweet ID, post ID, etc.
    text = Column(String)
    author = Column(String)
    url = Column(String)
    
    # LLM Classification scores (0-100)
    economic_score = Column(Float)
    crypto_score = Column(Float)
    privacy_score = Column(Float)
    instability_score = Column(Float)
    
    # Sentiment analysis
    sentiment = Column(String)  # 'bullish', 'bearish', 'neutral'
    confidence = Column(Float)  # 0-1
    overall_relevance = Column(Float)  # 0-100
    
    # Metadata
    summary = Column(String)
    key_entities = Column(JSON)
    engagement_score = Column(Float)  # Likes, retweets, etc.
    is_significant = Column(Boolean)
    
    # Processing
    processed_at = Column(DateTime, default=datetime.utcnow)
    classifier_model = Column(String)


class NewsSentiment(Base):
    """Aggregated news sentiment over time windows."""
    __tablename__ = 'news_sentiment'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    window_hours = Column(Integer)  # Aggregation window
    
    # Aggregated sentiment
    overall_sentiment = Column(Float)  # -100 to +100
    sentiment_strength = Column(Float)  # 0-100
    
    # Counts
    total_news_items = Column(Integer)
    significant_news_count = Column(Integer)
    bullish_count = Column(Integer)
    bearish_count = Column(Integer)
    neutral_count = Column(Integer)
    
    # Average category scores
    avg_economic_score = Column(Float)
    avg_crypto_score = Column(Float)
    avg_privacy_score = Column(Float)
    avg_instability_score = Column(Float)
    
    # Trading signal generated
    signal_generated = Column(Boolean, default=False)
    signal_type = Column(String)
    signal_strength = Column(Float)
    signal_confidence = Column(Float)
    
    # Metadata
    top_topics = Column(JSON)
    is_actionable = Column(Boolean)


def init_database():
    engine = create_engine(config.database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()