# News Monitoring Quick Start

Get the news monitoring system up and running in 5 minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

New dependencies added:
- `openai==1.12.0` - OpenAI GPT API
- `anthropic==0.18.1` - Anthropic Claude API

## Step 2: Get API Keys

### Twitter API (Required)

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create an app
3. Generate Bearer Token (v2 API)
4. Copy the token

### LLM API (Required - choose one)

**Option A - OpenAI (Recommended)**:
- Sign up at [OpenAI Platform](https://platform.openai.com/)
- Create API key
- Cost: ~$0.86/month for 30-min checks

**Option B - Anthropic**:
- Sign up at [Anthropic Console](https://console.anthropic.com/)
- Create API key
- Cost: ~$1.44/month for 30-min checks

## Step 3: Configure Environment

Add to your `.env` file:

```bash
# Twitter API
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAxxxxxxxxxxxxxxx

# LLM Provider (choose 'openai' or 'anthropic')
NEWS_LLM_PROVIDER=openai

# OpenAI (if using OpenAI)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx

# OR Anthropic (if using Anthropic)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx

# News Monitoring Settings
NEWS_MONITORING_ENABLED=true
NEWS_CHECK_INTERVAL_MINUTES=30
NEWS_AGGREGATION_WINDOW_HOURS=2
NEWS_STRATEGY_WEIGHT=0.10
```

## Step 4: Test the System

```bash
python test_news_monitoring.py
```

This will:
1. ✅ Test Twitter API connection
2. ✅ Test LLM classification
3. ✅ Test news aggregation
4. ✅ Test signal generation

**Expected output**:
```
Testing Twitter Client
✅ Found 10 tweets

Testing News Classifier
✅ Classification results:
  Economic Score: 85.0/100
  Crypto Score: 20.0/100
  Privacy Score: 15.0/100
  Instability Score: 60.0/100
  Sentiment: BEARISH
  
Testing News Aggregator
✅ Aggregated sentiment:
  Overall Sentiment: -23.4 (bearish)
  Is Actionable: false
  Significant News: 2
  
Testing News Sentiment Strategy
✅ Strategy Status: ok
⚪ No signal generated (sentiment not strong enough)
```

## Step 5: Run the Bot

```bash
# Paper trading mode
python run_bot.py --mode paper --capital 10000

# Or use Docker
docker-compose up -d
```

The news monitoring will:
- Run in the background
- Check Twitter every 30 minutes (configurable)
- Classify news using LLM
- Generate trading signals when sentiment is strong
- Send Telegram alerts for significant news

## How It Works

```
Every 30 minutes:
  1. Fetch tweets from 5 categories
     ├─ Crypto news
     ├─ Privacy news
     ├─ Economic news
     ├─ Instability news
     └─ Monero-specific
     
  2. Classify each tweet (LLM)
     ├─ Economic relevance (0-100)
     ├─ Crypto relevance (0-100)
     ├─ Privacy relevance (0-100)
     ├─ Instability relevance (0-100)
     └─ Sentiment (bullish/bearish/neutral)
     
  3. Aggregate sentiment
     ├─ Weight by confidence
     ├─ Boost privacy news 1.5x
     ├─ Boost instability 1.2x
     └─ Calculate overall: -100 to +100
     
  4. Generate signal (if actionable)
     ├─ Minimum sentiment: ±30
     ├─ Minimum significant news: 2
     └─ Strategy weight: 10%
```

## Signal Examples

### Bullish Signal

**News**: "EU mandates backdoors in encrypted messaging apps"

```
Classification:
  Privacy Score: 95
  Instability Score: 60
  Sentiment: BULLISH

Signal:
  Type: BUY
  Strength: 0.82
  Confidence: 0.78
  Weight in aggregation: 10%
```

### Bearish Signal

**News**: "Binance to delist Monero in compliance with regulation"

```
Classification:
  Crypto Score: 95
  Privacy Score: 80
  Sentiment: BEARISH

Signal:
  Type: SELL
  Strength: 0.68
  Confidence: 0.82
  Weight in aggregation: 10%
```

## Monitoring

### Check Sentiment

```python
from main import MoneroTradingBot

bot = MoneroTradingBot()
summary = bot.news_strategy.get_sentiment_summary()

print(f"Sentiment: {summary['overall_sentiment']:.1f}")
print(f"Actionable: {summary['is_actionable']}")
print(f"Top topics: {summary['top_topics']}")
```

### View in Database

```sql
-- Recent news events
SELECT timestamp, text, sentiment, privacy_score
FROM news_events
ORDER BY timestamp DESC
LIMIT 10;

-- Aggregated sentiment
SELECT timestamp, overall_sentiment, is_actionable
FROM news_sentiment
ORDER BY timestamp DESC
LIMIT 10;
```

### Telegram Alerts

You'll receive alerts for:
- ✅ Actionable sentiment (±50+)
- ✅ High privacy scores (80+)
- ✅ Significant news (3+ items)

## Customization

### Adjust Sensitivity

**More Conservative** (fewer signals):
```bash
NEWS_CHECK_INTERVAL_MINUTES=60  # Check less often
NEWS_STRATEGY_WEIGHT=0.05       # Lower weight
```

In code:
```python
NewsSentimentStrategy(
    min_sentiment_threshold=50,  # Stricter
    significant_news_min=3       # Require more news
)
```

**More Aggressive** (more signals):
```bash
NEWS_CHECK_INTERVAL_MINUTES=15  # Check more often
NEWS_STRATEGY_WEIGHT=0.15       # Higher weight
```

In code:
```python
NewsSentimentStrategy(
    min_sentiment_threshold=20,  # More lenient
    significant_news_min=1       # Fewer required
)
```

### Add Custom Queries

```python
# In main.py or after initialization
bot.news_strategy.news_aggregator.twitter_client.add_custom_query(
    name='monero_adoption',
    query='(Monero OR XMR) AND (adoption OR merchant OR payment) -is:retweet'
)
```

### Monitor Specific Accounts

```python
# Instead of broad queries
priority_accounts = [
    'edward_snowden',
    'wikileaks', 
    'TheBlock__',
    'CoinDesk'
]

for username in priority_accounts:
    tweets = await twitter_client.get_user_timeline(
        username=username,
        since_hours=2
    )
```

## Cost Estimate

**30-minute checks, 24/7**:
- ~2,880 classifications/month
- OpenAI GPT-4o-mini: ~$0.86/month
- Anthropic Claude Haiku: ~$1.44/month
- Twitter API: Free (500k tweets/month limit)

**Total**: < $2/month

## Troubleshooting

### "No news fetched"
- ✅ Check `TWITTER_BEARER_TOKEN` is set
- ✅ Verify token at developer.twitter.com
- ✅ Check rate limits

### "Classification failed"
- ✅ Check `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- ✅ Verify API quota/billing
- ✅ Check API status page

### "No signals generated"
- ⚪ This is normal! Most news is neutral
- ✅ Check `NEWS_MONITORING_ENABLED=true`
- ✅ Lower `min_sentiment_threshold`
- ✅ Check logs for sentiment scores

## Next Steps

1. ✅ Run `python test_news_monitoring.py`
2. ✅ Review classification results
3. ✅ Adjust thresholds if needed
4. ✅ Enable in production: `NEWS_MONITORING_ENABLED=true`
5. ✅ Monitor Telegram alerts
6. ✅ Review signals in Grafana dashboard

## Full Documentation

See [NEWS_MONITORING_GUIDE.md](NEWS_MONITORING_GUIDE.md) for:
- Architecture details
- Advanced customization
- Performance tuning
- Database queries
- Best practices

## Support

Issues? Questions?
- Check logs: `tail -f logs/trading_bot_*.log`
- Review test output: `python test_news_monitoring.py`
- Database: `SELECT * FROM news_events ORDER BY timestamp DESC LIMIT 10;`

---

**Built for**: Monero (XMR) swing trading  
**Focus**: Privacy and instability news (highest alpha for XMR)  
**Integration**: 10% weight in signal aggregation  
**Status**: Production-ready ✅

