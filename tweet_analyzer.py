#!/usr/bin/env python3
"""
Tweet Analyzer Module
Fetches and analyzes tweets from a specified Twitter/X account
"""

import tweepy
import pandas as pd
from datetime import datetime, timedelta
from textblob import TextBlob
from typing import List, Dict, Optional
import re


class TweetAnalyzer:
    """Analyzes tweets for patterns and sentiment"""
    
    def __init__(self, bearer_token: str, target_handle: str = "elonmusk"):
        """
        Initialize the Tweet Analyzer
        
        Args:
            bearer_token: Twitter API bearer token
            target_handle: Twitter handle to analyze (without @)
        """
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.target_handle = target_handle
        self.tweets_data = []
        
    def fetch_tweets(self, limit: int = 200) -> List[Dict]:
        """
        Fetch recent tweets from the target account
        
        Args:
            limit: Maximum number of tweets to fetch
            
        Returns:
            List of tweet dictionaries
        """
        try:
            # Get user ID
            user = self.client.get_user(username=self.target_handle)
            if not user.data:
                raise ValueError(f"User {self.target_handle} not found")
            
            user_id = user.data.id
            
            # Fetch tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(limit, 100),
                tweet_fields=['created_at', 'public_metrics', 'text'],
                exclude=['retweets', 'replies']
            )
            
            if not tweets.data:
                return []
            
            # Process tweets
            self.tweets_data = []
            for tweet in tweets.data:
                tweet_dict = {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                }
                self.tweets_data.append(tweet_dict)
            
            return self.tweets_data
            
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a tweet
        
        Args:
            text: Tweet text
            
        Returns:
            Dictionary with polarity and subjectivity scores
        """
        blob = TextBlob(text)
        return {
            'polarity': blob.sentiment.polarity,  # -1 to 1 (negative to positive)
            'subjectivity': blob.sentiment.subjectivity  # 0 to 1 (objective to subjective)
        }
    
    def detect_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """
        Detect specific keywords in tweet text
        
        Args:
            text: Tweet text
            keywords: List of keywords to search for
            
        Returns:
            List of found keywords
        """
        text_lower = text.lower()
        found_keywords = []
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        return found_keywords
    
    def analyze_patterns(self) -> pd.DataFrame:
        """
        Analyze patterns in fetched tweets
        
        Returns:
            DataFrame with analyzed tweet data
        """
        if not self.tweets_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.tweets_data)
        
        # Add sentiment analysis
        sentiments = [self.analyze_sentiment(text) for text in df['text']]
        df['polarity'] = [s['polarity'] for s in sentiments]
        df['subjectivity'] = [s['subjectivity'] for s in sentiments]
        
        # Extract time-based features
        df['hour'] = df['created_at'].dt.hour
        df['day_of_week'] = df['created_at'].dt.dayofweek
        df['date'] = df['created_at'].dt.date
        
        # Calculate engagement score
        df['engagement_score'] = df['likes'] + df['retweets'] * 2 + df['replies']
        
        return df
    
    def get_time_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analyze time-based posting patterns
        
        Args:
            df: DataFrame with analyzed tweets
            
        Returns:
            Dictionary with time pattern statistics
        """
        if df.empty:
            return {}
        
        patterns = {
            'most_active_hour': df['hour'].mode()[0] if not df['hour'].empty else None,
            'most_active_day': df['day_of_week'].mode()[0] if not df['day_of_week'].empty else None,
            'avg_tweets_per_day': len(df) / max(1, (df['created_at'].max() - df['created_at'].min()).days),
            'hourly_distribution': df['hour'].value_counts().to_dict(),
            'daily_distribution': df['day_of_week'].value_counts().to_dict(),
        }
        
        return patterns
    
    def identify_market_signals(self, df: pd.DataFrame, 
                                crypto_keywords: List[str],
                                stock_keywords: List[str],
                                positive_threshold: float = 0.3,
                                negative_threshold: float = -0.3) -> List[Dict]:
        """
        Identify potential market signals from tweets
        
        Args:
            df: DataFrame with analyzed tweets
            crypto_keywords: List of crypto-related keywords
            stock_keywords: List of stock-related keywords
            positive_threshold: Minimum polarity for positive signals
            negative_threshold: Maximum polarity for negative signals
            
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        for idx, row in df.iterrows():
            crypto_matches = self.detect_keywords(row['text'], crypto_keywords)
            stock_matches = self.detect_keywords(row['text'], stock_keywords)
            
            if crypto_matches or stock_matches:
                signal = {
                    'timestamp': row['created_at'],
                    'text': row['text'],
                    'polarity': row['polarity'],
                    'engagement_score': row['engagement_score'],
                    'crypto_keywords': crypto_matches,
                    'stock_keywords': stock_matches,
                    'signal_type': None,
                    'confidence': 0.0
                }
                
                # Determine signal type based on sentiment
                if row['polarity'] >= positive_threshold:
                    signal['signal_type'] = 'BULLISH'
                    signal['confidence'] = min(row['polarity'] * row['subjectivity'], 1.0)
                elif row['polarity'] <= negative_threshold:
                    signal['signal_type'] = 'BEARISH'
                    signal['confidence'] = min(abs(row['polarity']) * row['subjectivity'], 1.0)
                else:
                    signal['signal_type'] = 'NEUTRAL'
                    signal['confidence'] = 0.5
                
                # Boost confidence based on engagement
                engagement_boost = min(row['engagement_score'] / 100000, 0.2)
                signal['confidence'] = min(signal['confidence'] + engagement_boost, 1.0)
                
                signals.append(signal)
        
        return signals
