#!/usr/bin/env python3
"""
Pattern Detector Module
Detects historical patterns and correlations in tweet data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import Counter


class PatternDetector:
    """Detects patterns and trends in tweet data"""
    
    def __init__(self):
        """Initialize the Pattern Detector"""
        self.historical_data = pd.DataFrame()
    
    def load_historical_data(self, df: pd.DataFrame):
        """
        Load historical tweet data for pattern analysis
        
        Args:
            df: DataFrame with historical tweet data
        """
        self.historical_data = df.copy()
    
    def calculate_tweet_frequency(self, df: pd.DataFrame, window_hours: int = 24) -> Dict:
        """
        Calculate tweet frequency patterns
        
        Args:
            df: DataFrame with tweet data
            window_hours: Time window in hours for frequency calculation
            
        Returns:
            Dictionary with frequency statistics
        """
        if df.empty:
            return {}
        
        df_sorted = df.sort_values('created_at')
        time_diffs = df_sorted['created_at'].diff().dt.total_seconds() / 3600  # in hours
        
        frequency_stats = {
            'avg_hours_between_tweets': time_diffs.mean(),
            'median_hours_between_tweets': time_diffs.median(),
            'min_hours_between_tweets': time_diffs.min(),
            'max_hours_between_tweets': time_diffs.max(),
            'std_hours_between_tweets': time_diffs.std(),
        }
        
        return frequency_stats
    
    def detect_burst_activity(self, df: pd.DataFrame, threshold: int = 5, 
                             window_hours: int = 3) -> List[Dict]:
        """
        Detect periods of unusually high tweet activity (bursts)
        
        Args:
            df: DataFrame with tweet data
            threshold: Minimum tweets in window to count as burst
            window_hours: Time window in hours
            
        Returns:
            List of burst periods
        """
        if df.empty:
            return []
        
        df_sorted = df.sort_values('created_at')
        bursts = []
        
        for idx, row in df_sorted.iterrows():
            window_start = row['created_at']
            window_end = window_start + timedelta(hours=window_hours)
            
            tweets_in_window = df_sorted[
                (df_sorted['created_at'] >= window_start) & 
                (df_sorted['created_at'] < window_end)
            ]
            
            if len(tweets_in_window) >= threshold:
                bursts.append({
                    'start_time': window_start,
                    'end_time': window_end,
                    'tweet_count': len(tweets_in_window),
                    'avg_sentiment': tweets_in_window['polarity'].mean() if 'polarity' in tweets_in_window.columns else 0,
                    'tweets': tweets_in_window['text'].tolist()
                })
        
        # Remove duplicate overlapping bursts
        unique_bursts = []
        for burst in bursts:
            if not any(burst['start_time'] == ub['start_time'] for ub in unique_bursts):
                unique_bursts.append(burst)
        
        return unique_bursts
    
    def analyze_content_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Analyze content patterns in tweets
        
        Args:
            df: DataFrame with tweet data
            
        Returns:
            Dictionary with content pattern statistics
        """
        if df.empty:
            return {}
        
        # Extract common words (simple tokenization)
        all_words = []
        for text in df['text']:
            words = text.lower().split()
            # Filter out very short words and URLs
            words = [w for w in words if len(w) > 3 and not w.startswith('http')]
            all_words.extend(words)
        
        word_freq = Counter(all_words).most_common(20)
        
        # Analyze tweet lengths
        tweet_lengths = df['text'].str.len()
        
        patterns = {
            'avg_tweet_length': tweet_lengths.mean(),
            'median_tweet_length': tweet_lengths.median(),
            'common_words': word_freq,
            'avg_sentiment_polarity': df['polarity'].mean() if 'polarity' in df.columns else 0,
            'sentiment_volatility': df['polarity'].std() if 'polarity' in df.columns else 0,
        }
        
        return patterns
    
    def detect_sentiment_shifts(self, df: pd.DataFrame, 
                               window_size: int = 10,
                               shift_threshold: float = 0.5) -> List[Dict]:
        """
        Detect significant sentiment shifts in tweet patterns
        
        Args:
            df: DataFrame with tweet data
            window_size: Number of tweets to use for rolling average
            shift_threshold: Minimum change in sentiment to count as shift
            
        Returns:
            List of sentiment shift events
        """
        if df.empty or 'polarity' not in df.columns:
            return []
        
        df_sorted = df.sort_values('created_at')
        df_sorted['sentiment_rolling'] = df_sorted['polarity'].rolling(
            window=window_size, min_periods=1
        ).mean()
        
        shifts = []
        for i in range(window_size, len(df_sorted)):
            prev_sentiment = df_sorted.iloc[i-window_size:i]['polarity'].mean()
            curr_sentiment = df_sorted.iloc[i-window_size//2:i]['polarity'].mean()
            
            sentiment_change = curr_sentiment - prev_sentiment
            
            if abs(sentiment_change) >= shift_threshold:
                shifts.append({
                    'timestamp': df_sorted.iloc[i]['created_at'],
                    'previous_sentiment': prev_sentiment,
                    'current_sentiment': curr_sentiment,
                    'change': sentiment_change,
                    'direction': 'POSITIVE' if sentiment_change > 0 else 'NEGATIVE'
                })
        
        return shifts
    
    def correlate_with_timing(self, df: pd.DataFrame) -> Dict:
        """
        Analyze correlation between timing and engagement/sentiment
        
        Args:
            df: DataFrame with tweet data
            
        Returns:
            Dictionary with correlation statistics
        """
        if df.empty:
            return {}
        
        correlations = {}
        
        # Hour vs engagement
        if 'hour' in df.columns and 'engagement_score' in df.columns:
            hourly_engagement = df.groupby('hour')['engagement_score'].mean()
            correlations['best_engagement_hours'] = hourly_engagement.nlargest(3).index.tolist()
            correlations['worst_engagement_hours'] = hourly_engagement.nsmallest(3).index.tolist()
        
        # Hour vs sentiment
        if 'hour' in df.columns and 'polarity' in df.columns:
            hourly_sentiment = df.groupby('hour')['polarity'].mean()
            correlations['most_positive_hours'] = hourly_sentiment.nlargest(3).index.tolist()
            correlations['most_negative_hours'] = hourly_sentiment.nsmallest(3).index.tolist()
        
        # Day of week vs engagement
        if 'day_of_week' in df.columns and 'engagement_score' in df.columns:
            daily_engagement = df.groupby('day_of_week')['engagement_score'].mean()
            correlations['best_engagement_days'] = daily_engagement.nlargest(3).index.tolist()
        
        return correlations
    
    def generate_pattern_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate a comprehensive pattern analysis report
        
        Args:
            df: DataFrame with tweet data
            
        Returns:
            Dictionary with complete pattern analysis
        """
        report = {
            'frequency_patterns': self.calculate_tweet_frequency(df),
            'burst_periods': self.detect_burst_activity(df),
            'content_patterns': self.analyze_content_patterns(df),
            'sentiment_shifts': self.detect_sentiment_shifts(df),
            'timing_correlations': self.correlate_with_timing(df),
            'total_tweets_analyzed': len(df),
            'analysis_date': datetime.now().isoformat()
        }
        
        return report
