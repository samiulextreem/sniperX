#!/usr/bin/env python3
"""
Profit Signal Generator Module
Generates actionable profit signals based on detected patterns
"""

from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd


class ProfitSignalGenerator:
    """Generates trading/profit signals from tweet analysis"""
    
    def __init__(self, min_confidence: float = 0.7):
        """
        Initialize the Profit Signal Generator
        
        Args:
            min_confidence: Minimum confidence score for signals (0-1)
        """
        self.min_confidence = min_confidence
        self.signals = []
    
    def generate_signals(self, market_signals: List[Dict], 
                        pattern_report: Dict) -> List[Dict]:
        """
        Generate actionable profit signals
        
        Args:
            market_signals: List of market-related signals from tweets
            pattern_report: Pattern analysis report
            
        Returns:
            List of enhanced profit signals
        """
        enhanced_signals = []
        
        for signal in market_signals:
            if signal['confidence'] >= self.min_confidence:
                enhanced_signal = self._enhance_signal(signal, pattern_report)
                enhanced_signals.append(enhanced_signal)
        
        self.signals = enhanced_signals
        return enhanced_signals
    
    def _enhance_signal(self, signal: Dict, pattern_report: Dict) -> Dict:
        """
        Enhance a signal with additional context from pattern analysis
        
        Args:
            signal: Original market signal
            pattern_report: Pattern analysis report
            
        Returns:
            Enhanced signal dictionary
        """
        enhanced = signal.copy()
        
        # Add timing context
        hour = signal['timestamp'].hour
        timing_correlations = pattern_report.get('timing_correlations', {})
        
        if 'best_engagement_hours' in timing_correlations:
            enhanced['high_engagement_time'] = hour in timing_correlations['best_engagement_hours']
        
        # Add burst context
        burst_periods = pattern_report.get('burst_periods', [])
        enhanced['during_burst'] = any(
            burst['start_time'] <= signal['timestamp'] <= burst['end_time']
            for burst in burst_periods
        )
        
        # Calculate action recommendation
        enhanced['action'] = self._determine_action(enhanced)
        enhanced['urgency'] = self._calculate_urgency(enhanced)
        
        return enhanced
    
    def _determine_action(self, signal: Dict) -> str:
        """
        Determine recommended action based on signal
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Action recommendation string
        """
        if signal['signal_type'] == 'BULLISH':
            if signal.get('crypto_keywords'):
                return f"CONSIDER BUYING {', '.join(signal['crypto_keywords']).upper()}"
            elif signal.get('stock_keywords'):
                return f"CONSIDER BUYING {', '.join(signal['stock_keywords']).upper()}"
            else:
                return "MONITOR FOR BUYING OPPORTUNITY"
        
        elif signal['signal_type'] == 'BEARISH':
            if signal.get('crypto_keywords'):
                return f"CONSIDER SELLING {', '.join(signal['crypto_keywords']).upper()}"
            elif signal.get('stock_keywords'):
                return f"CONSIDER SELLING {', '.join(signal['stock_keywords']).upper()}"
            else:
                return "MONITOR FOR SELLING OPPORTUNITY"
        
        else:
            return "MONITOR - NO CLEAR SIGNAL"
    
    def _calculate_urgency(self, signal: Dict) -> str:
        """
        Calculate urgency level of signal
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Urgency level string
        """
        confidence = signal['confidence']
        during_burst = signal.get('during_burst', False)
        high_engagement = signal.get('high_engagement_time', False)
        
        urgency_score = confidence
        if during_burst:
            urgency_score += 0.15
        if high_engagement:
            urgency_score += 0.1
        
        if urgency_score >= 0.85:
            return "CRITICAL"
        elif urgency_score >= 0.7:
            return "HIGH"
        elif urgency_score >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def rank_signals(self, signals: Optional[List[Dict]] = None) -> List[Dict]:
        """
        Rank signals by confidence and urgency
        
        Args:
            signals: Optional list of signals to rank (uses stored signals if None)
            
        Returns:
            Sorted list of signals
        """
        signals_to_rank = signals if signals is not None else self.signals
        
        # Define urgency weights
        urgency_weights = {
            'CRITICAL': 4,
            'HIGH': 3,
            'MEDIUM': 2,
            'LOW': 1
        }
        
        # Sort by urgency then confidence
        ranked = sorted(
            signals_to_rank,
            key=lambda x: (urgency_weights.get(x.get('urgency', 'LOW'), 0), x['confidence']),
            reverse=True
        )
        
        return ranked
    
    def format_signal_report(self, signals: Optional[List[Dict]] = None) -> str:
        """
        Format signals into a readable report
        
        Args:
            signals: Optional list of signals to format (uses stored signals if None)
            
        Returns:
            Formatted report string
        """
        signals_to_report = signals if signals is not None else self.signals
        
        if not signals_to_report:
            return "No signals detected with sufficient confidence."
        
        ranked_signals = self.rank_signals(signals_to_report)
        
        report = []
        report.append("=" * 80)
        report.append("SNIPERX PROFIT SIGNALS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Signals: {len(ranked_signals)}")
        report.append("")
        
        for idx, signal in enumerate(ranked_signals, 1):
            report.append(f"\n[SIGNAL #{idx}] - {signal['urgency']} URGENCY")
            report.append("-" * 80)
            report.append(f"Timestamp: {signal['timestamp']}")
            report.append(f"Type: {signal['signal_type']}")
            report.append(f"Confidence: {signal['confidence']:.2%}")
            report.append(f"Action: {signal['action']}")
            
            if signal.get('crypto_keywords'):
                report.append(f"Crypto Keywords: {', '.join(signal['crypto_keywords'])}")
            if signal.get('stock_keywords'):
                report.append(f"Stock Keywords: {', '.join(signal['stock_keywords'])}")
            
            report.append(f"\nTweet Content:")
            report.append(f'"{signal["text"]}"')
            
            report.append(f"\nSentiment: {signal['polarity']:.3f}")
            report.append(f"Engagement Score: {signal['engagement_score']:,}")
            
            if signal.get('during_burst'):
                report.append("⚠️  Posted during high-activity burst period")
            if signal.get('high_engagement_time'):
                report.append("📈 Posted during high-engagement time window")
            
            report.append("")
        
        report.append("=" * 80)
        report.append("DISCLAIMER: These signals are for informational purposes only.")
        report.append("Always conduct your own research before making investment decisions.")
        report.append("=" * 80)
        
        return "\n".join(report)
