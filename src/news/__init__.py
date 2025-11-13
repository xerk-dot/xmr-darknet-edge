"""
News monitoring and sentiment analysis module for trading bot.

This module provides:
- Twitter API integration for real-time news monitoring
- LLM-based classification across multiple dimensions
- News aggregation and sentiment analysis
- Trading signal generation from news events
"""

from .twitter_client import TwitterClient
from .news_classifier import NewsClassifier
from .news_aggregator import NewsAggregator
from .news_sentiment_strategy import NewsSentimentStrategy

__all__ = [
    'TwitterClient',
    'NewsClassifier',
    'NewsAggregator',
    'NewsSentimentStrategy',
]
