"""
Health monitoring module
"""
from datetime import datetime

def mock_health_data():
    return {
        'timestamp': datetime.utcnow().isoformat(),
        'temperature': 72.0,
        'sleep_hours': 6.5,
        'energy_level': 7,
        'hydration': 85,
        'movement_minutes': 15
    }
