# Quick Reference - System Flow

## The Simple Version

Your bot has **TWO BRAINS** running simultaneously:

### Brain 1: Price Analysis (Main Loop)
**Runs**: Every 12 hours  
**Looks at**: BTC/XMR prices, technical indicators, correlations  
**Decides**: Should I buy/sell based on price patterns?

### Brain 2: News Analysis (Background Loop)  
**Runs**: Every 30 minutes  
**Looks at**: Twitter news, world events, crypto headlines  
**Decides**: Should I buy/sell based on news sentiment?

Both brains feed their opinions into a **Signal Aggregator** that makes the final decision.

---

## Visual Flow (Simplified)

```
┌─────────────────────────────────────────────────────────┐
│                    INPUTS (Data Sources)                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  📊 Exchange APIs     📰 Twitter API    🤖 LLM APIs     │
│  (Binance, Kraken)    (News feeds)     (GPT/Claude)    │
│                                                          │
└────────┬────────────────────┬────────────────┬──────────┘
         │                    │                │
         ▼                    ▼                ▼
┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐
│ Price Data      │  │ News Tweets     │  │ Classify     │
│ BTC + XMR       │  │ (raw text)      │  │ News         │
│ 30 days hourly  │  │                 │  │ (relevance)  │
└────────┬────────┘  └────────┬────────┘  └──────┬───────┘
         │                    │                   │
         ▼                    └───────┬───────────┘
┌─────────────────┐                  │
│ Feature         │                  ▼
│ Engineering     │         ┌────────────────────┐
│ (indicators)    │         │ News Aggregator    │
└────────┬────────┘         │ (sentiment score)  │
         │                  └────────┬───────────┘
         │                           │
         └────────┬──────────────────┘
                  ▼
         ┌────────────────────────────────────────┐
         │        STRATEGY LAYER                   │
         │                                          │
         │  ┌────────────┐  ┌────────────┐        │
         │  │ BTC Lag    │  │ News       │        │
         │  │ Strategy   │  │ Strategy   │        │
         │  │   40%      │  │   10%      │        │
         │  └─────┬──────┘  └─────┬──────┘        │
         │        │                │               │
         │  ┌─────┴──────────┬────┴──────┐        │
         │  │ Trend    Mean  │    ML     │        │
         │  │ Follow   Rev   │  Filter   │        │
         │  │ 12.5%   12.5%  │   25%     │        │
         │  └─────┬──────────┴───┬───────┘        │
         └────────┼───────────────┼────────────────┘
                  │               │
                  ▼               ▼
         ┌────────────────────────────────┐
         │    SIGNAL AGGREGATOR           │
         │  (Weighted voting)             │
         │  → BUY / SELL / HOLD          │
         └────────────┬───────────────────┘
                      │
                      ▼
         ┌────────────────────────────────┐
         │    RISK MANAGER                │
         │  • Position size (2% max)      │
         │  • Stop loss calculation       │
         │  • Portfolio limits (30%)      │
         │  → APPROVE or REJECT           │
         └────────────┬───────────────────┘
                      │
         ┌────────────┴──────────────┐
         │                           │
         ▼ APPROVED                  ▼ REJECTED
┌─────────────────┐         ┌────────────────┐
│  ORDER MANAGER  │         │   Log & Skip   │
│  Execute trade  │         └────────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│            OUTPUTS                          │
│  📊 Database   📈 Grafana   💬 Telegram    │
│  (history)     (charts)     (alerts)       │
└─────────────────────────────────────────────┘
```

---

## Strategy Weights (Current Configuration)

```
Total Signal = (each strategy's vote × weight)

┌──────────────────────────┬────────┬─────────────────┐
│ Strategy                 │ Weight │ Purpose         │
├──────────────────────────┼────────┼─────────────────┤
│ BTC Correlation          │  40%   │ Primary alpha   │
│ News Sentiment           │  10%   │ Event-driven    │
│ Trend Following          │ 12.5%  │ Momentum        │
│ Mean Reversion           │ 12.5%  │ Range-bound     │
│ XGBoost ML               │  25%   │ Confirmation    │
└──────────────────────────┴────────┴─────────────────┘
```

---

## Data Storage (Databases)

### PostgreSQL (Structured Data)
- `trades` - Trade history
- `positions` - Current positions
- `signals` - Signal history
- `news_events` - Individual news items with LLM classification
- `news_sentiment` - Aggregated news sentiment scores

### InfluxDB (Time-Series)
- Price history (OHLCV)
- Portfolio value over time

### Redis (Cache)
- Recent data cache
- Task queue

---

## Dependencies Map

### Core (Always Required)
```
MoneroTradingBot
├─ DataAggregator → Exchange APIs (Binance/Kraken)
├─ FeatureEngineer → Technical Indicators
├─ SignalAggregator
│  ├─ BTCCorrelationStrategy ✓
│  ├─ TrendFollowing ✓
│  ├─ MeanReversion ✓
│  └─ XGBoostML ✓
├─ RiskManager → Position sizing, stops
└─ OrderManager → Trade execution
```

### Optional (News Monitoring)
```
If NEWS_MONITORING_ENABLED=true:
└─ NewsSentimentStrategy
   └─ NewsAggregator
      ├─ TwitterClient → Twitter API
      └─ NewsClassifier → LLM API (OpenAI/Anthropic)
```

**If news disabled**: Bot rebalances weights across remaining strategies.

---

## Critical Files Map

```
Project Root
├─ main.py                    ← Main orchestrator (start here)
├─ config/config.py           ← Configuration from .env
├─ .env                       ← API keys and settings
│
├─ src/
│  ├─ data/
│  │  ├─ data_aggregator.py   ← Fetches price data
│  │  └─ exchange_client.py   ← CCXT wrapper
│  │
│  ├─ features/
│  │  ├─ feature_engineering.py  ← Technical indicators
│  │  └─ market_regime.py         ← Market classification
│  │
│  ├─ signals/
│  │  ├─ signal_aggregator.py         ← Combines all signals
│  │  ├─ btc_correlation_strategy.py  ← BTC lag strategy (40%)
│  │  ├─ trend_following.py           ← Trend strategy (12.5%)
│  │  ├─ ml_strategy.py               ← ML strategy (25%)
│  │  └─ base_strategy.py             ← Strategy interface
│  │
│  ├─ news/                      ← NEW MODULE
│  │  ├─ twitter_client.py       ← Fetch tweets
│  │  ├─ news_classifier.py      ← LLM classification
│  │  ├─ news_aggregator.py      ← Combine sentiment
│  │  └─ news_sentiment_strategy.py  ← Generate signals (10%)
│  │
│  ├─ risk/
│  │  ├─ risk_manager.py         ← Position sizing, approval
│  │  └─ stop_loss.py            ← Stop/TP calculation
│  │
│  ├─ execution/
│  │  └─ order_manager.py        ← Place orders
│  │
│  ├─ monitoring/
│  │  ├─ prometheus_metrics.py   ← Metrics export
│  │  └─ telegram_alerts.py      ← Notifications
│  │
│  └─ database/
│     └─ models.py               ← SQLAlchemy models
│
├─ test_btc_correlation.py   ← Test BTC strategy
├─ run_bot.py                 ← CLI entry point
│
└─ docs/
   ├─ ARCHITECTURE.md         ← Full technical architecture (THIS)
   ├─ QUICK_REFERENCE.md      ← Simplified guide
   └─ BTC_CORRELATION_FLOW.md ← BTC strategy details
```

---

## Configuration (.env)

### Essential (Core System)
```env
# Exchange APIs
BINANCE_API_KEY=xxx
BINANCE_SECRET=xxx
KRAKEN_API_KEY=xxx
KRAKEN_SECRET=xxx

# Database
POSTGRES_URL=postgresql://...
REDIS_URL=redis://...
INFLUXDB_URL=http://...

# Telegram
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

### Optional (News Monitoring)
```env
# Enable news monitoring
NEWS_MONITORING_ENABLED=true

# Twitter API
TWITTER_BEARER_TOKEN=xxx

# LLM Provider (choose one)
NEWS_LLM_PROVIDER=openai      # or 'anthropic'
OPENAI_API_KEY=xxx            # if using OpenAI
ANTHROPIC_API_KEY=xxx         # if using Anthropic

# News settings
NEWS_CHECK_INTERVAL_MINUTES=30
NEWS_AGGREGATION_WINDOW_HOURS=2
NEWS_STRATEGY_WEIGHT=0.10
```

---

## Startup Sequence

```
1. Load .env configuration
2. Connect to PostgreSQL
3. Connect to exchanges (Binance, Kraken)
4. Start Prometheus metrics server (port 8000)
5. Initialize Telegram bot
6. [Optional] Initialize news monitoring
   ├─ Connect to Twitter API
   └─ Initialize LLM client (GPT-4 or Claude)
7. Start main trading loop (12h cycle)
8. [Optional] Start news monitoring loop (30min cycle)
```

---

## Troubleshooting

### Bot runs but no trades execute
→ Check risk manager logs - likely rejection due to:
- Position size too large (>2%)
- Portfolio exposure too high (>30%)
- Signal strength below threshold

### News monitoring not working
→ Check `.env`:
- `NEWS_MONITORING_ENABLED=true`
- `TWITTER_BEARER_TOKEN` is set
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set

### No signals generated
→ Check:
- Exchange data is fetching correctly
- BTC correlation >0.6 (logged in console)
- News sentiment is updating (logged every 30min)

### High API costs
→ Adjust `.env`:
- Increase `NEWS_CHECK_INTERVAL_MINUTES` (default 30)
- Use `NEWS_LLM_PROVIDER=openai` with `gpt-4o-mini` (cheaper)

---

## Performance Monitoring

### Grafana Dashboard (http://localhost:3000)
- Portfolio value chart
- Win rate by strategy
- BTC-XMR correlation gauge
- News sentiment over time

### Prometheus Metrics (http://localhost:8000/metrics)
- `active_positions_count`
- `signals_generated_total{strategy="BTCCorrelation"}`
- `news_sentiment_score`
- `win_rate`

### Database Queries
```sql
-- Recent trades
SELECT * FROM trades ORDER BY created_at DESC LIMIT 10;

-- News sentiment history
SELECT * FROM news_sentiment ORDER BY window_start DESC LIMIT 20;

-- Strategy performance
SELECT strategy_name, COUNT(*), AVG(strength) 
FROM signals 
GROUP BY strategy_name;
```

---

## The Big Picture

**You have a multi-strategy ensemble system:**

1. **BTC lag** provides the primary edge (market inefficiency)
2. **News sentiment** catches event-driven moves (information edge)
3. **Traditional indicators** provide baseline signals (time-tested)
4. **ML** filters out bad trades (adaptive learning)

**All strategies vote, risk manager approves/rejects, orders execute.**

The architecture is complex because **you're combining 5 different alpha sources**. This is intentional for diversification, but it means more configuration and more potential issues.

**Key insight**: Each component is **modular** and **optional**. You can disable news monitoring and the bot still works. You can tune weights independently. You can add new strategies without changing core logic.

This is a **production-grade system**, not a simple script.

