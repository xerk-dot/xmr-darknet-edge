#!/usr/bin/env python3
"""
Simplified test to demonstrate the bot's ML regime detection capability
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import xgboost as xgb
from sklearn.preprocessing import StandardScaler

print("=" * 60)
print("MONERO TRADING BOT - ML REGIME DETECTION TEST")
print("=" * 60)

# Create sample data
dates = pd.date_range(start=datetime.now() - timedelta(days=60), end=datetime.now(), freq='1h')
price_series = 150 + np.random.randn(len(dates)).cumsum() * 2

df = pd.DataFrame({
    'close': np.abs(price_series),
    'volume': np.random.rand(len(dates)) * 1000000,
    'high': np.abs(price_series + abs(np.random.randn(len(dates))) * 2),
    'low': np.abs(price_series - abs(np.random.randn(len(dates))) * 2)
})

# Calculate simple features
df['returns'] = df['close'].pct_change()
df['volatility'] = df['returns'].rolling(20).std()
df['rsi'] = 50 + np.random.randn(len(dates)) * 20  # Simplified RSI
df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])

# Define market regimes based on volatility and trend
vol_percentile = df['volatility'].rolling(100).rank(pct=True)
trend = df['close'].rolling(20).mean().diff()

# Create regime labels (what we're trying to predict)
# 0 = ranging, 1 = trending_up, 2 = trending_down, 3 = high_volatility
conditions = [
    (vol_percentile > 0.8),  # High volatility
    (trend > 0) & (vol_percentile < 0.7),  # Trending up
    (trend < 0) & (vol_percentile < 0.7),  # Trending down
]
choices = [3, 1, 2]
df['regime'] = np.select(conditions, choices, default=0)

# Prepare features for XGBoost
feature_cols = ['returns', 'volatility', 'rsi', 'volume_ratio', 'price_position']
df_clean = df.dropna()

if len(df_clean) > 200:
    X = df_clean[feature_cols]
    y = df_clean['regime']

    # Split data
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train XGBoost model
    print("\n1. TRAINING XGBOOST FOR REGIME DETECTION")
    print("-" * 40)

    model = xgb.XGBClassifier(
        objective='multi:softprob',
        num_class=4,
        max_depth=4,
        learning_rate=0.1,
        n_estimators=50,
        random_state=42
    )

    model.fit(X_train_scaled, y_train, verbose=False)

    # Evaluate
    accuracy = model.score(X_test_scaled, y_test)
    print(f"Model Accuracy: {accuracy:.2%}")

    # Get feature importance
    importance = dict(zip(feature_cols, model.feature_importances_))
    print("\nFeature Importance:")
    for feat, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feat:15s}: {imp:.3f}")

    # Predict current regime
    latest_features = X.iloc[-1:].values
    latest_scaled = scaler.transform(latest_features)
    prediction = model.predict(latest_scaled)[0]
    probabilities = model.predict_proba(latest_scaled)[0]

    regime_map = {
        0: 'RANGING',
        1: 'TRENDING UP',
        2: 'TRENDING DOWN',
        3: 'HIGH VOLATILITY'
    }

    print("\n2. CURRENT MARKET REGIME DETECTION")
    print("-" * 40)
    print(f"Detected Regime: {regime_map[prediction]}")
    print(f"Confidence: {max(probabilities):.2%}")
    print("\nRegime Probabilities:")
    for i, regime in regime_map.items():
        print(f"  {regime:15s}: {probabilities[i]:.2%}")

    print("\n3. TRADING STRATEGY BASED ON REGIME")
    print("-" * 40)

    latest_rsi = df_clean['rsi'].iloc[-1]

    if prediction == 0:  # Ranging
        print("Strategy: MEAN REVERSION")
        if latest_rsi < 30:
            print("Signal: BUY (RSI oversold in ranging market)")
        elif latest_rsi > 70:
            print("Signal: SELL (RSI overbought in ranging market)")
        else:
            print("Signal: HOLD (Wait for extremes)")

    elif prediction == 1:  # Trending Up
        print("Strategy: MOMENTUM FOLLOWING")
        if latest_rsi < 40:
            print("Signal: BUY (Pullback in uptrend)")
        else:
            print("Signal: HOLD (Wait for pullback)")

    elif prediction == 2:  # Trending Down
        print("Strategy: SHORT OR STAY OUT")
        if latest_rsi > 60:
            print("Signal: SELL (Rally in downtrend)")
        else:
            print("Signal: HOLD (Avoid catching falling knife)")

    else:  # High Volatility
        print("Strategy: RISK OFF")
        print("Signal: STAY OUT (Too risky to trade)")

    print("\n4. HOW THE BOT WORKS")
    print("-" * 40)
    print("✓ Uses XGBoost to classify market into 4 regimes")
    print("✓ NOT trying to predict price (that usually fails)")
    print("✓ Different strategy for each regime:")
    print("  - Ranging → Mean reversion")
    print("  - Trending → Momentum")
    print("  - High Vol → Stay out")
    print("✓ This approach is more robust than price prediction")

else:
    print("Not enough data for training")

print("\n" + "=" * 60)