# News Monitoring System Guide

Comprehensive guide for the Twitter-based news monitoring and LLM classification system.

## Overview

The news monitoring system continuously tracks breaking news from Twitter and uses Large Language Models (LLMs) to classify and analyze news across 4 critical dimensions for privacy coin trading:

1. **Economic Relevance** (0-100): Central bank policy, inflation, recession signals
2. **Cryptocurrency Relevance** (0-100): Bitcoin, Monero, blockchain regulation
3. **Privacy Relevance** (0-100): Surveillance, encryption, data protection
4. **Instability Relevance** (0-100): Wars, sanctions, regulatory crackdowns

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  News Monitoring Flow                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Twitter API → TwitterClient → NewsClassifier (LLM)      │
│       ↓              ↓                ↓                  │
│  Fetch Tweets → Classify → Aggregate Sentiment           │
│                           ↓                               │
│                  NewsSentimentStrategy                   │
│                           ↓                               │
│                  Trading Signals (10% weight)            │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. TwitterClient (`src/news/twitter_client.py`)

**Purpose**: Fetch relevant tweets using Twitter API v2

**Features**:
- Pre-configured queries for crypto, privacy, economic, and instability news
- Monitors high-credibility accounts (CoinDesk, Reuters, Snowden, etc.)
- Extracts engagement metrics (likes, retweets, quotes)
- Deduplicates and filters retweets/replies

**Key Methods**:
```python
# Fetch news from all categories
news = await twitter_client.fetch_all_news(
    since_hours=2,
    max_per_category=50
)

# Add custom query
twitter_client.add_custom_query(
    name='custom_topic',
    query='Monero AND (regulation OR ban) -is:retweet'
)

# Monitor specific user
tweets = await twitter_client.get_user_timeline(
    username='edward_snowden',
    since_hours=24
)
```

### 2. NewsClassifier (`src/news/news_classifier.py`)

**Purpose**: LLM-based classification of news across 4 dimensions

**Supported LLM Providers**:
- **OpenAI**: GPT-4o-mini (recommended, $0.30/1K classifications)
- **Anthropic**: Claude 3 Haiku ($0.50/1K classifications)

**Classification Output**:
```json
{
  "economic_score": 85,
  "crypto_score": 90,
  "privacy_score": 75,
  "instability_score": 40,
  "sentiment": "bullish",
  "confidence": 85,
  "overall_relevance": 82.5,
  "key_entities": ["Bitcoin", "SEC", "Regulation"],
  "summary": "SEC delays Bitcoin ETF decision",
  "is_significant": true
}
```

**Key Methods**:
```python
# Classify single news item
classification = await news_classifier.classify_news(
    news_text="Breaking: Fed announces rate hike...",
    metadata={'author': {...}, 'created_at': ...}
)

# Batch classification (up to 5 concurrent)
results = await news_classifier.classify_batch(
    news_items=[...],
    max_concurrent=5
)
```

### 3. NewsAggregator (`src/news/news_aggregator.py`)

**Purpose**: Aggregate classified news and generate sentiment scores

**Features**:
- Caches classified news (24h expiry)
- Aggregates sentiment over time windows (default: 2h)
- Applies privacy and instability boosts for XMR
- Tracks sentiment history and trends

**Sentiment Calculation**:
- Range: -100 (very bearish) to +100 (very bullish)
- Privacy news boost: 1.5x (privacy concerns = bullish for XMR)
- Instability boost: 1.2x (wars, sanctions = bullish for XMR)
- Weighted by confidence and relevance

**Key Methods**:
```python
# Fetch, classify, and aggregate
sentiment = await news_aggregator.update_and_aggregate(
    since_hours=2
)

# Get sentiment trend
trend = news_aggregator.get_sentiment_trend(hours=24)
# Returns: {'trend': 'improving', 'average_sentiment': 45.2, ...}
```

### 4. NewsSentimentStrategy (`src/news/news_sentiment_strategy.py`)

**Purpose**: Generate trading signals from news sentiment

**Signal Generation Rules**:
- Minimum sentiment strength: 30 (configurable)
- Minimum significant news items: 2
- Signal strength boosted by privacy/instability scores
- Confidence based on news consensus and significance

**Integration with Bot**:
```python
# In main.py, strategy is automatically initialized if config is set
# Runs in background loop, checks every 30 minutes (configurable)

# Get current sentiment
summary = news_strategy.get_sentiment_summary()

# Get detailed breakdown
breakdown = news_strategy.get_detailed_breakdown()
```

## Setup Instructions

### 1. Get Twitter API Access

1. Apply at [Twitter Developer Portal](https://developer.twitter.com/)
2. Create a new app
3. Generate Bearer Token (API v2 access)
4. Add to `.env`:
   ```
   TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxxxxxxxxxxx
   ```

**Rate Limits** (Free tier):
- 500,000 tweets/month
- ~200 tweets per request
- Adequate for monitoring every 30 minutes

### 2. Get LLM API Access

**Option A - OpenAI (Recommended)**:
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Create API key
3. Add to `.env`:
   ```
   NEWS_LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Option B - Anthropic Claude**:
1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Create API key
3. Add to `.env`:
   ```
   NEWS_LLM_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Cost Estimates** (per month, 30-min checks):
- ~2,880 classifications/month
- OpenAI GPT-4o-mini: ~$0.86/month
- Anthropic Claude Haiku: ~$1.44/month

### 3. Configure Settings

In `.env`:
```bash
# Enable news monitoring
NEWS_MONITORING_ENABLED=true

# Check interval (minutes)
NEWS_CHECK_INTERVAL_MINUTES=30

# Time window for aggregating news (hours)
NEWS_AGGREGATION_WINDOW_HOURS=2

# Strategy weight in signal aggregation (0.0-1.0)
NEWS_STRATEGY_WEIGHT=0.10

# Auto-select model (or specify: gpt-4o-mini, claude-3-haiku, etc.)
NEWS_LLM_MODEL=
```

## Monitored News Categories

### 1. Crypto General
- Bitcoin price movements
- Major exchange news
- Blockchain developments
- Altcoin regulations

**Example queries**:
- "Bitcoin breaks $50k"
- "Binance announces XMR delisting"
- "SEC sues crypto exchange"

### 2. Privacy News
- Surveillance expansions
- Encryption legislation
- Data breaches
- Privacy coin regulations

**Example queries**:
- "EU passes surveillance law"
- "WhatsApp encryption backdoor"
- "Privacy coin ban proposed"

### 3. Economic News
- Fed rate decisions
- Inflation reports
- Recession signals
- GDP announcements

**Example queries**:
- "Fed raises rates by 0.5%"
- "Inflation hits 8%"
- "ECB emergency meeting"

### 4. Instability News
- Wars and conflicts
- Financial sanctions
- Banking crises
- Regulatory crackdowns

**Example queries**:
- "Russia sanctions escalate"
- "Bank run in [country]"
- "Capital controls imposed"

### 5. Monero Specific
- XMR listings/delistings
- Monero regulations
- Privacy tech developments
- XMR price movements

**Example queries**:
- "Kraken lists XMR"
- "Monero audit complete"
- "XMR hard fork successful"

## Signal Examples

### Bullish Signals

**Privacy Concerns**:
```
News: "EU mandates backdoors in encrypted messaging"
Classification:
  - Privacy Score: 95
  - Instability Score: 60
  - Sentiment: Bullish (privacy demand increases)
Signal: BUY, Strength: 0.82, Confidence: 0.78
```

**Banking Instability**:
```
News: "Major bank failure triggers withdrawal limits"
Classification:
  - Instability Score: 90
  - Economic Score: 85
  - Sentiment: Bullish (flight to crypto)
Signal: BUY, Strength: 0.75, Confidence: 0.70
```

**Regulatory Overreach**:
```
News: "Government announces mandatory KYC for all transactions"
Classification:
  - Privacy Score: 88
  - Crypto Score: 75
  - Sentiment: Bullish (privacy coins benefit)
Signal: BUY, Strength: 0.79, Confidence: 0.74
```

### Bearish Signals

**Exchange Delisting**:
```
News: "Binance to delist Monero in compliance with regulation"
Classification:
  - Crypto Score: 95
  - Privacy Score: 80
  - Sentiment: Bearish (liquidity impact)
Signal: SELL, Strength: 0.68, Confidence: 0.82
```

**Direct Ban**:
```
News: "Country X bans privacy coin transactions"
Classification:
  - Crypto Score: 90
  - Privacy Score: 85
  - Sentiment: Bearish (market restriction)
Signal: SELL, Strength: 0.72, Confidence: 0.76
```

### Neutral (No Signal)

**General Crypto News**:
```
News: "Bitcoin price analysis: $45k resistance"
Classification:
  - Crypto Score: 60
  - Privacy Score: 10
  - Sentiment: Neutral
Signal: None (below significance threshold)
```

## Monitoring and Debugging

### Check Current Sentiment

```python
# Get summary
summary = bot.news_strategy.get_sentiment_summary()
print(f"Sentiment: {summary['overall_sentiment']:.1f}")
print(f"Actionable: {summary['is_actionable']}")
print(f"Top topics: {summary['top_topics']}")

# Get detailed breakdown
breakdown = bot.news_strategy.get_detailed_breakdown()
print(f"Primary driver: {breakdown['primary_driver']}")
print(f"Trend (24h): {breakdown['trend_24h']['trend']}")
```

### Database Queries

```sql
-- View recent classified news
SELECT 
    timestamp,
    text,
    sentiment,
    privacy_score,
    crypto_score,
    is_significant
FROM news_events
ORDER BY timestamp DESC
LIMIT 10;

-- View aggregated sentiment over time
SELECT 
    timestamp,
    overall_sentiment,
    significant_news_count,
    is_actionable
FROM news_sentiment
ORDER BY timestamp DESC
LIMIT 20;

-- Find high-impact privacy news
SELECT 
    timestamp,
    text,
    privacy_score,
    sentiment,
    summary
FROM news_events
WHERE privacy_score >= 70
ORDER BY privacy_score DESC
LIMIT 10;
```

### Telegram Alerts

News sentiment alerts are sent when:
- Sentiment becomes actionable (≥3 significant items)
- Overall sentiment crosses ±50 threshold
- Privacy score ≥80 (critical for XMR)
- Instability score ≥80 (major events)

**Alert Format**:
```
📰 Significant news detected!
Sentiment: +67.3
Significant items: 5
Top news: EU passes encryption backdoor law, expected to boost privacy coin demand
Categories: Privacy (92), Instability (68), Crypto (75)
```

## Customization

### Add Custom News Sources

```python
# In your bot initialization or config
twitter_client.add_custom_query(
    name='custom_monero',
    query='(Monero OR XMR) AND (adoption OR integration) -is:retweet'
)
```

### Adjust Classification Prompt

Edit `src/news/news_classifier.py`, method `_build_classification_prompt()`:
```python
# Add custom instructions or emphasis
prompt += "\nIMPORTANT: Pay special attention to privacy implications for Monero."
```

### Change Strategy Parameters

```python
# In main.py or when initializing
news_strategy = NewsSentimentStrategy(
    news_aggregator=news_aggregator,
    min_sentiment_threshold=40,  # Stricter threshold
    significant_news_min=3,      # Require more significant news
    privacy_boost_multiplier=2.0, # Higher privacy boost
    instability_boost_multiplier=1.5
)
```

### Adjust Strategy Weight

```python
# In main.py
strategy_weights = {
    'BTCCorrelation': 0.35,  # Reduce BTC weight
    'NewsSentiment': 0.15,   # Increase news weight to 15%
    'TrendFollowing': 0.125,
    'MeanReversion': 0.125,
    'XGBoostML': 0.25
}
```

## Performance Tuning

### Reduce API Costs

1. **Increase check interval**: 60 minutes instead of 30
2. **Reduce max_per_category**: 30 instead of 50
3. **Use cheaper model**: GPT-4o-mini or Claude Haiku
4. **Cache more aggressively**: Increase cache expiry to 48h

### Improve Signal Quality

1. **Stricter thresholds**: Increase `min_sentiment_threshold` to 40-50
2. **More significant news required**: Set `significant_news_min` to 3-4
3. **Focus on priority sources**: Filter by `is_priority_source`
4. **Shorter time windows**: Reduce to 1h for fresher signals

### Monitor Specific Accounts Only

```python
# Instead of broad queries, monitor specific high-quality accounts
priority_accounts = [
    'edward_snowden', 'EFF', 'wikileaks',
    'CoinDesk', 'Cointelegraph', 'TheBlock__'
]

for username in priority_accounts:
    tweets = await twitter_client.get_user_timeline(
        username=username,
        since_hours=2
    )
```

## Troubleshooting

### No News Fetched

**Check**:
- Twitter API token is valid
- API rate limits not exceeded
- Queries are returning results (test at developer.twitter.com)

**Debug**:
```python
# Test Twitter connection
news = await twitter_client.search_recent_tweets(
    query='Bitcoin',
    max_results=10,
    since_hours=24
)
print(f"Found {len(news)} tweets")
```

### Classification Errors

**Check**:
- LLM API key is valid
- API quota not exceeded
- Response format is valid JSON

**Debug**:
```python
# Test classification
result = await news_classifier.classify_news(
    "Fed raises interest rates",
    metadata={}
)
print(result)
```

### No Signals Generated

**Check**:
- `NEWS_MONITORING_ENABLED=true`
- News sentiment is being updated (check logs)
- Thresholds aren't too strict
- Sentiment meets actionability criteria

**Debug**:
```python
# Check sentiment
summary = news_strategy.get_sentiment_summary()
print(f"Status: {summary['status']}")
print(f"Sentiment: {summary.get('overall_sentiment', 0):.1f}")
print(f"Actionable: {summary.get('is_actionable', False)}")
```

### High API Costs

**Solutions**:
1. Increase `NEWS_CHECK_INTERVAL_MINUTES` to 60
2. Reduce `max_per_category` to 20-30
3. Use GPT-4o-mini (cheapest option)
4. Set `NEWS_MONITORING_ENABLED=false` during testing

## Best Practices

### 1. Start Conservative

- Begin with `NEWS_STRATEGY_WEIGHT=0.05` (5%)
- Increase gradually as you validate signals
- Monitor false positives/negatives

### 2. Combine with Other Strategies

- News alone shouldn't drive trades
- Use as confirmation for BTC correlation
- Weight news higher during volatile periods

### 3. Monitor News Quality

- Check `significant_news_count` regularly
- Review `top_topics` for relevance
- Validate that high-scoring news actually impacts XMR

### 4. Adjust for Market Conditions

- Increase news weight during regulatory uncertainty
- Decrease during quiet periods
- Monitor sentiment trends, not just absolute values

### 5. Privacy/Instability Focus

- These categories are most relevant for XMR
- Consider boosting their multipliers
- Track correlation between privacy news and XMR price

## Example Integration

Complete example of using the news monitoring system:

```python
from src.news.twitter_client import TwitterClient
from src.news.news_classifier import NewsClassifier
from src.news.news_aggregator import NewsAggregator
from src.news.news_sentiment_strategy import NewsSentimentStrategy

# Initialize components
twitter = TwitterClient(bearer_token="YOUR_TOKEN")
classifier = NewsClassifier(provider="openai", api_key="YOUR_KEY")
aggregator = NewsAggregator(twitter, classifier, aggregation_window_hours=2)
strategy = NewsSentimentStrategy(aggregator)

# Update sentiment (call periodically)
await strategy.update_sentiment()

# Generate signal
signal = strategy.generate_signal(df)  # df = OHLCV data

if signal:
    print(f"Signal: {signal.signal_type}")
    print(f"Strength: {signal.strength:.3f}")
    print(f"Confidence: {signal.confidence:.3f}")
    print(f"Top news: {signal.metadata['top_news'][0]}")

# Get sentiment report
report = strategy.get_detailed_breakdown()
print(f"Primary driver: {report['primary_driver']}")
print(f"Direction: {report['direction']}")
print(f"24h trend: {report['trend_24h']['trend']}")
```

## Advanced Features

### Multi-Source Support (Future)

The architecture supports adding more news sources:
- Reddit (r/Monero, r/CryptoCurrency, r/privacy)
- News RSS feeds (CoinDesk, Cointelegraph)
- Telegram channels
- Discord servers

### Real-Time Streaming (Future)

Twitter API v2 supports filtered streams:
```python
# Stream tweets in real-time matching filters
await twitter_client.start_filtered_stream(
    rules=['Monero OR XMR', 'privacy regulation']
)
```

### Sentiment Prediction (Future)

Use historical sentiment to predict market moves:
- Train model on sentiment → price correlation
- Identify leading indicators (which news predicts price best)
- Optimize category weights based on historical performance

## References

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Anthropic Claude Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

---

**Note**: This system is designed for educational and research purposes. Always validate signals against other indicators and practice proper risk management.

