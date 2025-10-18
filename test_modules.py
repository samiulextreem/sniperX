#!/usr/bin/env python3
"""
Example script demonstrating SniperX functionality with mock data
This shows how the modules work without requiring API credentials
"""

import sys
from datetime import datetime, timedelta
import pandas as pd
from textblob import TextBlob

from tweet_analyzer import TweetAnalyzer
from pattern_detector import PatternDetector
from profit_signal import ProfitSignalGenerator


def generate_mock_tweets():
    """Generate mock tweet data for testing"""
    base_time = datetime.now() - timedelta(days=7)
    
    mock_tweets = [
        {
            'id': 1,
            'text': 'Bitcoin is the future of money! 🚀',
            'created_at': base_time + timedelta(hours=0),
            'likes': 50000,
            'retweets': 10000,
            'replies': 5000
        },
        {
            'id': 2,
            'text': 'Tesla is doing great this quarter',
            'created_at': base_time + timedelta(hours=3),
            'likes': 30000,
            'retweets': 5000,
            'replies': 2000
        },
        {
            'id': 3,
            'text': 'Dogecoin to the moon! Much wow!',
            'created_at': base_time + timedelta(hours=6),
            'likes': 80000,
            'retweets': 15000,
            'replies': 8000
        },
        {
            'id': 4,
            'text': 'Working on exciting new things at Tesla and SpaceX',
            'created_at': base_time + timedelta(hours=12),
            'likes': 40000,
            'retweets': 8000,
            'replies': 3000
        },
        {
            'id': 5,
            'text': 'Ethereum has interesting technology',
            'created_at': base_time + timedelta(hours=24),
            'likes': 45000,
            'retweets': 9000,
            'replies': 4000
        },
        {
            'id': 6,
            'text': 'Amazing progress on Starship! 🚀',
            'created_at': base_time + timedelta(hours=36),
            'likes': 60000,
            'retweets': 12000,
            'replies': 6000
        },
        {
            'id': 7,
            'text': 'Crypto is the future',
            'created_at': base_time + timedelta(hours=48),
            'likes': 55000,
            'retweets': 11000,
            'replies': 5500
        },
    ]
    
    return mock_tweets


def test_sentiment_analysis():
    """Test sentiment analysis on sample tweets"""
    print("\n" + "=" * 80)
    print("TESTING SENTIMENT ANALYSIS")
    print("=" * 80)
    
    sample_texts = [
        "Bitcoin is the future of money! 🚀",
        "Dogecoin to the moon! Much wow!",
        "This is terrible news for the market",
        "Just an average day"
    ]
    
    # We'll use TextBlob directly since we don't need the full analyzer
    for text in sample_texts:
        blob = TextBlob(text)
        sentiment = blob.sentiment
        print(f"\nText: \"{text}\"")
        print(f"  Polarity: {sentiment.polarity:.3f} (negative to positive: -1 to 1)")
        print(f"  Subjectivity: {sentiment.subjectivity:.3f} (objective to subjective: 0 to 1)")
        
        if sentiment.polarity > 0.3:
            print(f"  → BULLISH signal")
        elif sentiment.polarity < -0.3:
            print(f"  → BEARISH signal")
        else:
            print(f"  → NEUTRAL")


def test_pattern_detection():
    """Test pattern detection with mock data"""
    print("\n" + "=" * 80)
    print("TESTING PATTERN DETECTION")
    print("=" * 80)
    
    mock_tweets = generate_mock_tweets()
    
    # Create DataFrame and add sentiment
    df = pd.DataFrame(mock_tweets)
    sentiments = [TextBlob(text).sentiment for text in df['text']]
    df['polarity'] = [s.polarity for s in sentiments]
    df['subjectivity'] = [s.subjectivity for s in sentiments]
    
    # Add time features
    df['hour'] = df['created_at'].dt.hour
    df['day_of_week'] = df['created_at'].dt.dayofweek
    df['date'] = df['created_at'].dt.date
    df['engagement_score'] = df['likes'] + df['retweets'] * 2 + df['replies']
    
    # Test pattern detector
    detector = PatternDetector()
    
    # Frequency patterns
    freq_patterns = detector.calculate_tweet_frequency(df)
    print("\nTweet Frequency Patterns:")
    print(f"  Average hours between tweets: {freq_patterns.get('avg_hours_between_tweets', 0):.2f}")
    print(f"  Median hours between tweets: {freq_patterns.get('median_hours_between_tweets', 0):.2f}")
    
    # Burst detection
    bursts = detector.detect_burst_activity(df, threshold=2, window_hours=12)
    print(f"\nBurst Periods Detected: {len(bursts)}")
    for i, burst in enumerate(bursts[:3], 1):  # Show first 3
        print(f"  Burst #{i}: {burst['tweet_count']} tweets in {burst['start_time']} - {burst['end_time']}")
    
    # Content patterns
    content = detector.analyze_content_patterns(df)
    print(f"\nContent Patterns:")
    print(f"  Average tweet length: {content.get('avg_tweet_length', 0):.0f} characters")
    print(f"  Average sentiment: {content.get('avg_sentiment_polarity', 0):.3f}")
    print(f"  Top words: {[word for word, count in content.get('common_words', [])[:5]]}")


def test_signal_generation():
    """Test profit signal generation"""
    print("\n" + "=" * 80)
    print("TESTING SIGNAL GENERATION")
    print("=" * 80)
    
    mock_tweets = generate_mock_tweets()
    
    # Create DataFrame and add analysis
    df = pd.DataFrame(mock_tweets)
    sentiments = [TextBlob(text).sentiment for text in df['text']]
    df['polarity'] = [s.polarity for s in sentiments]
    df['subjectivity'] = [s.subjectivity for s in sentiments]
    df['hour'] = df['created_at'].dt.hour
    df['day_of_week'] = df['created_at'].dt.dayofweek
    df['engagement_score'] = df['likes'] + df['retweets'] * 2 + df['replies']
    
    # Create pattern report
    detector = PatternDetector()
    pattern_report = detector.generate_pattern_report(df)
    
    # Create market signals (simplified)
    crypto_keywords = ['bitcoin', 'btc', 'ethereum', 'eth', 'dogecoin', 'doge', 'crypto']
    stock_keywords = ['tesla', 'tsla', 'stock', 'shares']
    
    market_signals = []
    for idx, row in df.iterrows():
        text_lower = row['text'].lower()
        crypto_matches = [k for k in crypto_keywords if k in text_lower]
        stock_matches = [k for k in stock_keywords if k in text_lower]
        
        if crypto_matches or stock_matches:
            signal = {
                'timestamp': row['created_at'],
                'text': row['text'],
                'polarity': row['polarity'],
                'engagement_score': row['engagement_score'],
                'crypto_keywords': crypto_matches,
                'stock_keywords': stock_matches,
                'signal_type': 'BULLISH' if row['polarity'] > 0.3 else 'NEUTRAL',
                'confidence': min(row['polarity'] * row['subjectivity'] + 
                                min(row['engagement_score'] / 100000, 0.2), 1.0)
            }
            market_signals.append(signal)
    
    # Generate profit signals
    signal_gen = ProfitSignalGenerator(min_confidence=0.3)
    profit_signals = signal_gen.generate_signals(market_signals, pattern_report)
    
    print(f"\nGenerated {len(profit_signals)} profit signals")
    print("\nTop 3 Signals:")
    
    ranked = signal_gen.rank_signals(profit_signals)
    for i, signal in enumerate(ranked[:3], 1):
        print(f"\n  Signal #{i}:")
        print(f"    Type: {signal['signal_type']}")
        print(f"    Confidence: {signal['confidence']:.2%}")
        print(f"    Urgency: {signal['urgency']}")
        print(f"    Action: {signal['action']}")
        print(f"    Tweet: \"{signal['text'][:50]}...\"")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("SNIPERX MODULE TESTS")
    print("Testing core functionality with mock data")
    print("=" * 80)
    
    try:
        test_sentiment_analysis()
        test_pattern_detection()
        test_signal_generation()
        
        print("\n" + "=" * 80)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print("\nThe SniperX modules are working correctly!")
        print("To use with real data, configure your Twitter API credentials in config.ini")
        print("and run: python sniperx.py --analyze")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
