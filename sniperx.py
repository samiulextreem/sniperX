#!/usr/bin/env python3
"""
SniperX - Main CLI Application
Analyzes Elon Musk's tweet patterns to identify potential profit opportunities
"""

import argparse
import configparser
import sys
import os
from datetime import datetime
import json

from tweet_analyzer import TweetAnalyzer
from pattern_detector import PatternDetector
from profit_signal import ProfitSignalGenerator


def load_config(config_path: str = 'config.ini') -> configparser.ConfigParser:
    """
    Load configuration from file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        ConfigParser object
    """
    config = configparser.ConfigParser()
    
    if not os.path.exists(config_path):
        print(f"Error: Configuration file '{config_path}' not found.")
        print("Please copy 'config.example.ini' to 'config.ini' and fill in your API credentials.")
        sys.exit(1)
    
    config.read(config_path)
    return config


def parse_keyword_list(keyword_string: str) -> list:
    """Parse comma-separated keyword string into list"""
    return [k.strip() for k in keyword_string.split(',') if k.strip()]


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='SniperX - Analyze Elon Musk tweet patterns for profit opportunities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sniperx.py --analyze                    # Run full analysis
  python sniperx.py --analyze --limit 100        # Analyze last 100 tweets
  python sniperx.py --analyze --output report.json  # Save report to file
        """
    )
    
    parser.add_argument(
        '--analyze', '-a',
        action='store_true',
        help='Run tweet analysis'
    )
    
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=None,
        help='Number of tweets to analyze (default: from config)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.ini',
        help='Path to configuration file (default: config.ini)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default=None,
        help='Output file for JSON report (optional)'
    )
    
    parser.add_argument(
        '--min-confidence',
        type=float,
        default=None,
        help='Minimum confidence for signals (0-1, default: from config)'
    )
    
    parser.add_argument(
        '--target',
        type=str,
        default=None,
        help='Twitter handle to analyze (default: from config)'
    )
    
    args = parser.parse_args()
    
    if not args.analyze:
        parser.print_help()
        sys.exit(0)
    
    # Load configuration
    print("Loading configuration...")
    config = load_config(args.config)
    
    # Get configuration values
    bearer_token = config.get('twitter', 'bearer_token')
    target_handle = args.target or config.get('analysis', 'target_handle', fallback='elonmusk')
    tweet_limit = args.limit or config.getint('analysis', 'tweet_limit', fallback=200)
    min_confidence = args.min_confidence or config.getfloat('analysis', 'min_confidence', fallback=0.7)
    
    crypto_keywords = parse_keyword_list(
        config.get('trading', 'crypto_keywords', fallback='bitcoin,btc,ethereum,eth,dogecoin,doge,crypto')
    )
    stock_keywords = parse_keyword_list(
        config.get('trading', 'stock_keywords', fallback='tesla,tsla,stock,shares')
    )
    
    positive_threshold = config.getfloat('trading', 'positive_threshold', fallback=0.3)
    negative_threshold = config.getfloat('trading', 'negative_threshold', fallback=-0.3)
    
    # Validate bearer token
    if bearer_token == 'your_bearer_token_here':
        print("\n" + "=" * 80)
        print("ERROR: Twitter API credentials not configured!")
        print("=" * 80)
        print("\nPlease update config.ini with your Twitter API credentials.")
        print("Get them from: https://developer.twitter.com/en/portal/dashboard")
        print("\nFor demo purposes, we'll generate a simulated report with sample data.")
        print("=" * 80 + "\n")
        
        # Generate demo output
        generate_demo_report()
        sys.exit(0)
    
    # Initialize components
    print(f"\nInitializing SniperX Tweet Analyzer...")
    print(f"Target: @{target_handle}")
    print(f"Tweet Limit: {tweet_limit}")
    print(f"Min Confidence: {min_confidence}")
    
    analyzer = TweetAnalyzer(bearer_token=bearer_token, target_handle=target_handle)
    pattern_detector = PatternDetector()
    signal_generator = ProfitSignalGenerator(min_confidence=min_confidence)
    
    # Fetch tweets
    print(f"\nFetching tweets from @{target_handle}...")
    tweets = analyzer.fetch_tweets(limit=tweet_limit)
    
    if not tweets:
        print("Error: No tweets fetched. Please check your API credentials and target handle.")
        sys.exit(1)
    
    print(f"✓ Fetched {len(tweets)} tweets")
    
    # Analyze patterns
    print("\nAnalyzing tweet patterns...")
    df = analyzer.analyze_patterns()
    print(f"✓ Analyzed {len(df)} tweets")
    
    # Detect patterns
    print("\nDetecting behavioral patterns...")
    pattern_report = pattern_detector.generate_pattern_report(df)
    
    time_patterns = analyzer.get_time_patterns(df)
    print(f"✓ Most active hour: {time_patterns.get('most_active_hour', 'N/A')}")
    print(f"✓ Average tweets per day: {time_patterns.get('avg_tweets_per_day', 0):.2f}")
    
    # Identify market signals
    print("\nIdentifying market signals...")
    market_signals = analyzer.identify_market_signals(
        df,
        crypto_keywords=crypto_keywords,
        stock_keywords=stock_keywords,
        positive_threshold=positive_threshold,
        negative_threshold=negative_threshold
    )
    print(f"✓ Found {len(market_signals)} market-related tweets")
    
    # Generate profit signals
    print("\nGenerating profit signals...")
    profit_signals = signal_generator.generate_signals(market_signals, pattern_report)
    print(f"✓ Generated {len(profit_signals)} high-confidence signals")
    
    # Display report
    print("\n")
    report_text = signal_generator.format_signal_report(profit_signals)
    print(report_text)
    
    # Save to file if requested
    if args.output:
        output_data = {
            'analysis_metadata': {
                'timestamp': datetime.now().isoformat(),
                'target_handle': target_handle,
                'tweets_analyzed': len(df),
                'signals_generated': len(profit_signals)
            },
            'time_patterns': time_patterns,
            'pattern_report': {
                'frequency_patterns': pattern_report.get('frequency_patterns', {}),
                'total_bursts': len(pattern_report.get('burst_periods', [])),
                'content_patterns': pattern_report.get('content_patterns', {}),
                'sentiment_shifts': len(pattern_report.get('sentiment_shifts', [])),
                'timing_correlations': pattern_report.get('timing_correlations', {})
            },
            'profit_signals': profit_signals
        }
        
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"\n✓ Report saved to {args.output}")
    
    print("\n" + "=" * 80)
    print("Analysis complete!")
    print("=" * 80)


def generate_demo_report():
    """Generate a demo report with sample data for demonstration"""
    from datetime import datetime, timedelta
    
    print("\n" + "=" * 80)
    print("SNIPERX DEMO REPORT - SAMPLE DATA")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNOTE: This is simulated data for demonstration purposes.")
    print("Configure your Twitter API credentials in config.ini for real analysis.")
    print("\n" + "=" * 80)
    
    # Sample patterns
    print("\nDETECTED PATTERNS:")
    print("-" * 80)
    print("✓ Most active posting hour: 2 AM UTC (Late night tweets)")
    print("✓ Average tweets per day: 12.5")
    print("✓ Tweet frequency pattern: Increased activity during market hours")
    print("✓ Detected 3 burst periods (5+ tweets within 3 hours)")
    print("✓ Average sentiment: Slightly positive (0.15)")
    print("✓ Sentiment volatility: Moderate (0.45)")
    
    print("\nSAMPLE PROFIT SIGNALS:")
    print("-" * 80)
    
    sample_signals = [
        {
            'urgency': 'CRITICAL',
            'type': 'BULLISH',
            'confidence': 0.87,
            'keywords': ['Dogecoin', 'DOGE'],
            'action': 'CONSIDER BUYING DOGECOIN',
            'tweet': 'Dogecoin is the future of currency!',
            'timestamp': datetime.now() - timedelta(hours=2)
        },
        {
            'urgency': 'HIGH',
            'type': 'BULLISH',
            'confidence': 0.75,
            'keywords': ['Bitcoin', 'BTC'],
            'action': 'CONSIDER BUYING BITCOIN',
            'tweet': 'Bitcoin looking strong',
            'timestamp': datetime.now() - timedelta(hours=5)
        }
    ]
    
    for idx, signal in enumerate(sample_signals, 1):
        print(f"\n[SIGNAL #{idx}] - {signal['urgency']} URGENCY")
        print("-" * 80)
        print(f"Type: {signal['type']}")
        print(f"Confidence: {signal['confidence']:.2%}")
        print(f"Action: {signal['action']}")
        print(f"Keywords: {', '.join(signal['keywords'])}")
        print(f"Tweet: \"{signal['tweet']}\"")
        print(f"Timestamp: {signal['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n" + "=" * 80)
    print("DISCLAIMER: These are SAMPLE signals for demonstration only.")
    print("Configure Twitter API credentials for real analysis.")
    print("=" * 80)


if __name__ == '__main__':
    main()
