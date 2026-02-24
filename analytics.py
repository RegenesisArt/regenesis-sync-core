"""
Advanced analytics for CMHP
"""
from datetime import datetime, timedelta
import random

class CMHPAnalytics:
    def __init__(self):
        self.data_history = []
        
    def add_data_point(self, system, metric, value):
        """Add data point to history"""
        self.data_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'system': system,
            'metric': metric,
            'value': value
        })
        # Keep only last 1000 points
        if len(self.data_history) > 1000:
            self.data_history = self.data_history[-1000:]
    
    def predict_sales(self, historical_data):
        """Predict future sales"""
        if not historical_data:
            return {'prediction': 'insufficient_data', 'confidence': 0}
        
        # Simple linear prediction
        last_week = sum([d.get('value', 0) for d in historical_data[-7:]])
        avg_daily = last_week / 7 if last_week > 0 else 0
        
        predictions = {
            'next_7_days': round(avg_daily * 7, 2),
            'next_30_days': round(avg_daily * 30, 2),
            'confidence': min(80, len(historical_data) * 10),
            'based_on': f'{len(historical_data)} data points'
        }
        return predictions
    
    def optimal_posting_times(self, engagement_data):
        """Calculate optimal posting times"""
        # Mock optimal times based on typical engagement
        optimal_times = [
            {'platform': 'instagram', 'times': ['9:00 AM', '12:00 PM', '7:00 PM']},
            {'platform': 'twitter', 'times': ['8:00 AM', '3:00 PM', '6:00 PM']},
            {'platform': 'youtube', 'times': ['5:00 PM', '8:00 PM']},
            {'platform': 'tiktok', 'times': ['12:00 PM', '4:00 PM', '9:00 PM']}
        ]
        return optimal_times
    
    def health_correlation(self, health_data, productivity_data):
        """Correlate health with productivity"""
        if not health_data or not productivity_data:
            return {'analysis': 'need_more_data'}
        
        # Simple correlation
        avg_energy = sum([h.get('energy', 5) for h in health_data]) / len(health_data)
        avg_productivity = sum([p.get('output', 5) for p in productivity_data]) / len(productivity_data)
        
        correlation = min(1.0, avg_energy / 10 * avg_productivity / 10)
        
        return {
            'energy_productivity_correlation': round(correlation, 2),
            'recommendation': 'Increase energy to boost productivity' if correlation < 0.7 else 'Optimal balance maintained',
            'avg_energy': round(avg_energy, 1),
            'avg_productivity': round(avg_productivity, 1)
        }
    
    def generate_report(self, period_days=7):
        """Generate analytics report"""
        report = {
            'period': f'last_{period_days}_days',
            'timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'data_points_analyzed': len(self.data_history),
                'systems_monitored': set([d['system'] for d in self.data_history]),
                'time_range': 'unknown' if not self.data_history else 
                    f"{self.data_history[0]['timestamp'][:10]} to {self.data_history[-1]['timestamp'][:10]}"
            },
            'recommendations': [
                'Post more process content (highest engagement)',
                'Optimize listing times for eBay (Sunday evenings)',
                'Maintain energy above 7/10 for maximum creativity'
            ]
        }
        return report

# Global instance
analytics = CMHPAnalytics()
