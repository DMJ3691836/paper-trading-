# Pine Script Indicator Setup Guide

## Paper Trading Webhook Signals - PVSRA / EMA / Confluence

This Pine Script indicator generates trading signals based on Volume Spread Reversal Analysis (PVSRA), EMA alignment, and confluence levels, then sends them to your Python trading bot via webhooks.

---

## 📋 Features

✅ **PVSRA Signals**
- Green Vector: Bullish volume continuation
- Red Vector: Bearish volume continuation
- Blue Vector: Accumulation phases
- Reversal patterns (Red→Green, Green→Red)

✅ **EMA-Based Confirmations**
- 5/13/50/200 EMA alignment tracking
- Bullish alignment: 5 > 13 > 50 > 200
- Bearish alignment: 5 < 13 < 50 < 200

✅ **Confluence Levels**
- Daily Pivot Points (PP, R1, R2, S1, S2)
- Average Daily Range (ADR)
- Psychological Price Levels
- FX Market Session Detection (Asia, London, New York)

✅ **JSON Webhook Integration**
- Real-time signal delivery
- Complete indicator data in payload
- Trigger control (bar close vs real-time)

---

## 🚀 Installation

### Step 1: Copy the Indicator Code

1. Go to [TradingView Editor](https://www.tradingview.com/pine-script-editor/)
2. Create a new script
3. Copy the entire code from `paper_trading_webhook_signals.pine`
4. Paste it into the editor
5. Click **Save** and name it: `Paper Trading Webhook Signals`

### Step 2: Add to Chart

1. Open any chart on TradingView
2. Click **Indicators** (bottom toolbar)
3. Search for "Paper Trading Webhook Signals"
4. Click to add to chart

### Step 3: Configure Indicator Settings

#### Signal Settings
- **Volume MA Length**: 20 (bars for volume average)
- **Vector Volume Multiple**: 1.8 (minimum volume multiple for signals)
- **Trigger Only On Bar Close**: ON (recommended)

#### EMA Settings
- **EMA Fast**: 5
- **EMA Mid**: 13
- **EMA Trend**: 50
- **EMA Long**: 200

#### Confluence Levels
- **ADR Length**: 14 (days for average daily range)
- **Psychological Level Step**: 0.0050 (e.g., 0.50 pips for EURUSD)

#### Sessions (UTC times)
- **Asia Session**: 0000-0700
- **London Session**: 0700-1200
- **New York Session**: 1200-1700

#### Webhook Settings
- **Send Webhook Alerts**: ON
- **Show Signal Labels**: ON (optional, for visual reference)

---

## 🔔 Webhook Configuration

### Setting Up Alerts in TradingView

1. Click the **Alert** bell icon on the chart
2. Click **Create Alert**
3. In the **Condition** dropdown, select your indicator
4. Choose **Webhook Signal** condition
5. In **Webhook URL**, enter your bot's webhook endpoint:

```
https://your-server-url.com/webhook
```

### Example Webhook URL
- **Local Testing**: `http://localhost:5000/webhook`
- **Cloud Deployment**: `https://your-domain.com/webhook`

### Alert Configuration
- **Frequency**: Once per bar close
- **Show notification**: Optional

---

## 📊 JSON Payload Format

When a signal triggers, the indicator sends a JSON payload like:

```json
{
  "symbol": "EURUSD",
  "signal": "GREEN_VECTOR",
  "direction": "BUY",
  "price": 1.085,
  "time": "2026-05-15T12:30:00Z",
  "indicators": {
    "pvsra_color": "green",
    "volume_multiple": 1.8,
    "ema_5": 1.086,
    "ema_13": 1.0855,
    "ema_50": 1.0845,
    "ema_200": 1.082,
    "pivot_pp": 1.0835,
    "pivot_r1": 1.088,
    "pivot_r2": 1.091,
    "pivot_s1": 1.0805,
    "pivot_s2": 1.0775,
    "adr_high": 1.089,
    "adr_low": 1.074,
    "adr_50_high": 1.0815,
    "adr_50_low": 1.0815,
    "session": "LONDON",
    "psy_hi": 1.095,
    "psy_lo": 1.07
  }
}
```

### Payload Fields Explained

| Field | Description | Example |
|-------|-------------|---------|
| `symbol` | Trading pair | EURUSD |
| `signal` | Signal type | GREEN_VECTOR, RED_VECTOR, etc. |
| `direction` | Trade direction | BUY, SELL, BUY_STRONG, SELL_STRONG |
| `price` | Current price | 1.085 |
| `time` | UTC timestamp | 2026-05-15T12:30:00Z |
| `pvsra_color` | Volume color | green, red, neutral |
| `volume_multiple` | Volume vs MA ratio | 1.8 |
| `ema_*` | EMA values | 1.086, 1.0855, etc. |
| `pivot_*` | Pivot levels | R1, R2, S1, S2, PP |
| `adr_*` | ADR levels | high, low, 50% levels |
| `session` | Current session | LONDON, NEW_YORK, ASIA, OFF_SESSION |
| `psy_*` | Psychology levels | high and low boundaries |

---

## 📈 Signal Types & Confidence

### Tier 1: Reversals (Confidence: 9.5)
- **RED_TO_GREEN_REVERSAL**: Previous candle RED, current GREEN
  - Action: BUY_STRONG
- **GREEN_TO_RED_REVERSAL**: Previous candle GREEN, current RED
  - Action: SELL_STRONG

### Tier 2: Vectors (Confidence: 8-9)
- **GREEN_VECTOR**: Bullish candle + high volume
  - Action: BUY
- **RED_VECTOR**: Bearish candle + high volume
  - Action: SELL

### Tier 3: EMA Alignment (Confidence: 8)
- **EMA_BULLISH_ALIGN**: 5 > 13 > 50 > 200 (fresh signal)
  - Action: BUY
- **EMA_BEARISH_ALIGN**: 5 < 13 < 50 < 200 (fresh signal)
  - Action: SELL

---

## 🎯 How to Use With Your Python Bot

1. **Ensure bot is running**:
   ```bash
   python bot/webhook_handler.py
   ```

2. **Add indicator to chart** with your webhook URL

3. **Monitor signals** in:
   - TradingView chart (visual labels)
   - Bot dashboard: `http://localhost:5000/dashboard`
   - Logs: `signals.log`

4. **The bot automatically**:
   - Validates signal confidence
   - Calculates confluence score
   - Sizes position (2% risk)
   - Executes entry/exit logic

---

## 🔧 Customization Tips

### Change Volume Threshold
- **Increase** "Vector Volume Multiple" (e.g., 2.0) → more strict, fewer signals
- **Decrease** "Vector Volume Multiple" (e.g., 1.5) → more lenient, more signals

### Change EMA Periods
- **Faster**: Use 3/7/21/100 for more responsive signals
- **Slower**: Use 8/21/89/200 for fewer, higher-quality signals

### Adjust Psychological Level Step
- **EURUSD**: 0.0050 (50 pips)
- **GBPUSD**: 0.0100 (100 pips)
- **XAU/USD (Gold)**: 10.0 (per $10)

### Session Times
- Adjust UTC times based on your timezone
- Example: For GMT+1, add 1 hour to all times

---

## ⚠️ Important Notes

- **Volume Data**: Forex pairs may have varying volume data; ensure your broker supports volume reporting
- **Timeframe**: Test on 15-min, 30-min, or 1H charts; adjust for your style
- **Lookahead**: Uses previous day's pivot data (safe for intraday trading)
- **Testing**: Backtest with your bot before live trading
- **Webhook Latency**: Network delays may affect alert delivery

---

## 🐛 Troubleshooting

### Indicator Not Showing
- Verify Pine Script v6 compatibility
- Clear cache: Ctrl+Shift+Del → Clear all site data
- Reload page

### No Signals Triggering
- Check "Send Webhook Alerts" is ON
- Verify "Trigger Only On Bar Close" matches your preference
- Monitor volume: may need to adjust Vector Volume Multiple
- Check chart timeframe (works on all)

### Webhook Not Received
- Verify bot is running on correct port
- Check webhook URL is correct and accessible
- Monitor TradingView alert status
- Review bot logs: `tail -f signals.log`

### Payload Format Issues
- Ensure bot webhook handler expects this JSON schema
- Check bot `webhook_handler.py` for expected fields
- Verify signal names match bot's signal processor

---

## 📚 Documentation References

- [COMPLETE_SIGNAL_MAPPING.md](../docs/COMPLETE_SIGNAL_MAPPING.md) - All signal types and confluence scoring
- [webhook_handler.py](../bot/webhook_handler.py) - Python bot receiver
- [signal_processor.py](../bot/signal_processor.py) - Signal validation logic

---

## 💡 Best Practices

1. **Start with high confidence signals** (Reversals and strong Vectors)
2. **Use confluence** - combine multiple signal types
3. **Respect session times** - strongest signals in London/NY sessions
4. **Monitor ADR** - use for stop loss and target placement
5. **Test backtest results** before live trading
6. **Use 2% risk per trade** as recommended by the bot

---

**Happy Trading! 📈🚀**
