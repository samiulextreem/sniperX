# SniperX - Elon Tweet Pattern Analyzer 🎯

SniperX is an advanced tool that analyzes Elon Musk's tweet patterns to identify potential profit opportunities in cryptocurrency and stock markets. By analyzing tweet sentiment, timing, frequency, and content patterns, SniperX generates actionable trading signals.

## Features

- 🐦 **Tweet Analysis**: Fetches and analyzes tweets from Elon Musk's Twitter/X account
- 📊 **Pattern Detection**: Identifies behavioral patterns including:
  - Posting frequency and timing patterns
  - Burst activity periods (unusual tweet volume)
  - Sentiment shifts and trends
  - Engagement correlations
- 💰 **Profit Signals**: Generates actionable trading signals with:
  - Confidence scores
  - Urgency levels (Critical, High, Medium, Low)
  - Specific action recommendations
  - Keyword detection (crypto and stock mentions)
- 🎯 **Smart Analysis**: Uses sentiment analysis and historical patterns to improve signal accuracy
- 📈 **Comprehensive Reports**: Detailed reports in both text and JSON formats

## Installation

### Prerequisites

- Python 3.8 or higher
- Twitter/X API Developer Account ([Get one here](https://developer.twitter.com/en/portal/dashboard))

### Setup

1. Clone the repository:
```bash
git clone https://github.com/samiulextreem/sniperX.git
cd sniperX
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API credentials:
```bash
cp config.example.ini config.ini
```

4. Edit `config.ini` and add your Twitter API credentials:
```ini
[twitter]
bearer_token = your_bearer_token_here
```

## Usage

### Basic Analysis

Run a complete analysis of Elon's recent tweets:

```bash
python sniperx.py --analyze
```

### Advanced Options

```bash
# Analyze specific number of tweets
python sniperx.py --analyze --limit 100

# Set custom confidence threshold
python sniperx.py --analyze --min-confidence 0.8

# Save results to JSON file
python sniperx.py --analyze --output report.json

# Analyze a different account
python sniperx.py --analyze --target elonmusk

# Use custom config file
python sniperx.py --analyze --config my_config.ini
```

### Demo Mode

If you don't have API credentials yet, you can run in demo mode to see sample output:

```bash
python sniperx.py --analyze
```

The tool will detect missing credentials and generate a simulated report.

## Configuration

The `config.ini` file allows you to customize analysis parameters:

### Twitter API Settings
```ini
[twitter]
bearer_token = your_bearer_token_here
```

### Analysis Settings
```ini
[analysis]
target_handle = elonmusk      # Twitter handle to analyze
tweet_limit = 200              # Number of tweets to fetch
min_confidence = 0.7           # Minimum signal confidence (0-1)
```

### Trading Keywords
```ini
[trading]
crypto_keywords = bitcoin,btc,ethereum,eth,dogecoin,doge,crypto
stock_keywords = tesla,tsla,stock,shares
positive_threshold = 0.3       # Sentiment threshold for bullish signals
negative_threshold = -0.3      # Sentiment threshold for bearish signals
```

## How It Works

### 1. Tweet Collection
- Fetches recent tweets from the target account using Twitter API v2
- Filters out retweets and replies to focus on original content

### 2. Pattern Analysis
- **Frequency Analysis**: Calculates tweet posting patterns over time
- **Burst Detection**: Identifies periods of unusually high activity
- **Content Analysis**: Extracts common themes and keywords
- **Sentiment Tracking**: Monitors sentiment changes and shifts
- **Timing Correlation**: Analyzes relationship between posting time and engagement

### 3. Signal Generation
- Detects mentions of crypto or stock keywords
- Analyzes sentiment polarity (positive/negative)
- Calculates confidence based on:
  - Sentiment strength and subjectivity
  - Engagement metrics (likes, retweets, replies)
  - Timing patterns (high-engagement hours)
  - Burst activity correlation
- Ranks signals by urgency and confidence

### 4. Report Generation
- Produces actionable signals with clear recommendations
- Provides context including tweet content and timing
- Highlights high-priority signals

## Output Example

```
================================================================================
SNIPERX PROFIT SIGNALS REPORT
================================================================================
Generated: 2025-10-18 13:30:45
Total Signals: 3

[SIGNAL #1] - CRITICAL URGENCY
--------------------------------------------------------------------------------
Timestamp: 2025-10-18 02:15:30
Type: BULLISH
Confidence: 87.50%
Action: CONSIDER BUYING DOGECOIN, DOGE

Crypto Keywords: dogecoin, doge

Tweet Content:
"Dogecoin is the people's crypto!"

Sentiment: 0.650
Engagement Score: 125,430
⚠️  Posted during high-activity burst period
📈 Posted during high-engagement time window
================================================================================
```

## Understanding Signals

### Signal Types
- **BULLISH**: Positive sentiment, suggests buying opportunity
- **BEARISH**: Negative sentiment, suggests selling opportunity
- **NEUTRAL**: Mixed or unclear sentiment, monitor situation

### Urgency Levels
- **CRITICAL** (85%+): High confidence, immediate attention recommended
- **HIGH** (70-84%): Strong signal, timely action suggested
- **MEDIUM** (50-69%): Moderate signal, monitor closely
- **LOW** (<50%): Weak signal, informational only

### Confidence Score
Calculated based on:
- Sentiment strength and subjectivity
- Engagement metrics (normalized)
- Timing factors (burst periods, high-engagement hours)

## Modules

### tweet_analyzer.py
- Twitter API integration
- Tweet fetching and parsing
- Sentiment analysis
- Keyword detection
- Market signal identification

### pattern_detector.py
- Frequency pattern analysis
- Burst activity detection
- Content pattern analysis
- Sentiment shift detection
- Timing correlation analysis

### profit_signal.py
- Signal enhancement with pattern context
- Action recommendation generation
- Urgency calculation
- Signal ranking and formatting

### sniperx.py
- Main CLI application
- Configuration management
- Workflow orchestration
- Report generation

## Important Disclaimers

⚠️ **IMPORTANT**: This tool is for informational and educational purposes only.

- **Not Financial Advice**: Signals generated are based on tweet analysis only and should not be considered financial advice
- **Do Your Own Research**: Always conduct thorough research before making any investment decisions
- **Market Risk**: Cryptocurrency and stock markets are highly volatile and risky
- **No Guarantees**: Past patterns do not guarantee future results
- **Use Responsibly**: This tool does not guarantee profits and you can lose money

## API Rate Limits

Twitter API has rate limits:
- **Bearer Token Authentication**: 450 requests per 15-minute window
- **Tweet Lookup**: 300 requests per 15-minute window

The tool is designed to work within these limits for typical usage.

## Troubleshooting

### "No tweets fetched"
- Check your bearer token is correct
- Verify the target handle exists and is public
- Check your API access level (need v2 access)

### "Configuration file not found"
- Make sure you copied `config.example.ini` to `config.ini`
- Check the file is in the same directory as `sniperx.py`

### "Rate limit exceeded"
- Wait 15 minutes before retrying
- Reduce the `tweet_limit` in config

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License

This project is provided as-is for educational purposes.

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions

---

**Remember**: Always invest responsibly and never invest more than you can afford to lose. This tool is a research aid, not a crystal ball. 🎯