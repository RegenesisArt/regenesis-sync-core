"""
Health monitoring for CMHP Pillar 1
"""
from datetime import datetime
import random

class HealthTracker:
    def __init__(self):
        self.mock_data = {
            'temperature': 72.0,
            'sleep_hours': 6.5,
            'energy_level': 7,
            'hydration': 85,
            'movement_minutes': 15,
            'last_meal': '4 hours ago'
        }
    
    def get_health_status(self):
        """Get current health metrics"""
        status = self.mock_data.copy()
        status['timestamp'] = datetime.utcnow().isoformat()
        status['vitality_score'] = self._calculate_vitality()
        status['health_alert'] = self._check_alerts()
        return status
    
    def _calculate_vitality(self):
        """Calculate vitality score (0-100)"""
        temp_score = min(100, (self.mock_data['temperature'] - 68) * 20)
        sleep_score = min(100, self.mock_data['sleep_hours'] * 12.5)
        energy_score = self.mock_data['energy_level'] * 10
        return int((temp_score + sleep_score + energy_score) / 3)
    
    def _check_alerts(self):
        """Check for health alerts"""
        alerts = []
        if self.mock_data['temperature'] < 68:
            alerts.append('CRITICAL: Temperature below 68°F')
        if self.mock_data['sleep_hours'] < 6:
            alerts.append('WARNING: Sleep under 6 hours')
        if self.mock_data['energy_level'] < 5:
            alerts.append('WARNING: Energy below 5/10')
        return alerts if alerts else ['All good']

# Global instance
health_tracker = HealthTracker()
