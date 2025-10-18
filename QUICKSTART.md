# Quick Start Guide

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/samiulextreem/sniperX.git
cd sniperX
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure credentials:**
```bash
cp config.example.ini config.ini
# Edit config.ini and add your Twitter API bearer token
```

## Getting Twitter API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app or use an existing one
3. Navigate to "Keys and Tokens"
4. Copy your Bearer Token
5. Paste it in `config.ini` under `[twitter]` section

## Usage Examples

### Demo Mode (No Credentials Required)

Run without API credentials to see how it works:

```bash
python sniperx.py --analyze
```

### Full Analysis (Requires API Credentials)

```bash
# Analyze latest 200 tweets (default)
python sniperx.py --analyze

# Analyze specific number of tweets
python sniperx.py --analyze --limit 100

# Save results to JSON file
python sniperx.py --analyze --output results.json

# Use higher confidence threshold
python sniperx.py --analyze --min-confidence 0.8
```

### Test the Modules

Run the test suite with mock data:

```bash
python test_modules.py
```

## Understanding the Output

### Signal Types
- **BULLISH** 📈: Positive sentiment, potential buy signal
- **BEARISH** 📉: Negative sentiment, potential sell signal
- **NEUTRAL** ⚖️: Mixed sentiment, monitor only

### Urgency Levels
- **CRITICAL**: >85% confidence - Act immediately
- **HIGH**: 70-85% confidence - Consider action soon
- **MEDIUM**: 50-70% confidence - Monitor closely
- **LOW**: <50% confidence - Informational only

### What to Look For

1. **High Engagement Tweets**: More likes/retweets = more market impact
2. **Burst Periods**: Multiple tweets in short time = increased attention
3. **Positive Sentiment + Crypto Keywords**: Potential price pump
4. **Negative Sentiment + Stock Keywords**: Potential price drop

## Tips for Best Results

1. **Run regularly**: Tweet impact is time-sensitive
2. **Cross-reference**: Don't rely on signals alone - verify with other sources
3. **Set alerts**: Use cron/task scheduler for automatic analysis
4. **Adjust thresholds**: Tune confidence levels based on your risk tolerance
5. **Monitor patterns**: Historical patterns help predict future impacts

## Safety Reminders

⚠️ **IMPORTANT**:
- This is NOT financial advice
- Always do your own research
- Never invest more than you can afford to lose
- Past patterns don't guarantee future results
- Markets are unpredictable and risky

## Troubleshooting

**"No tweets fetched"**
- Verify your bearer token is correct
- Check the target handle is public
- Ensure you have Twitter API v2 access

**"Rate limit exceeded"**
- Wait 15 minutes before retrying
- Reduce the tweet limit in config

**"Module not found"**
- Make sure all dependencies are installed: `pip install -r requirements.txt`

## Advanced Configuration

Edit `config.ini` to customize:

- **target_handle**: Change to analyze different accounts
- **tweet_limit**: Adjust number of tweets to fetch
- **crypto_keywords**: Add/remove cryptocurrency keywords
- **stock_keywords**: Add/remove stock-related keywords
- **min_confidence**: Adjust signal sensitivity

## Support

For issues or questions, open an issue on GitHub.
