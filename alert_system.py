"""
Alert system for CMHP automation
"""
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

class AlertSystem:
    def __init__(self):
        self.alerts_sent = []
    
    def send_alert(self, level, message, system):
        """Send alert (mock for now, real email later)"""
        alert = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,  # info, warning, critical
            'message': message,
            'system': system,
            'sent_via': 'mock'
        }
        self.alerts_sent.append(alert)
        
        print(f"🔔 ALERT [{level.upper()}] {system}: {message}")
        return alert
    
    def check_health_alerts(self, health_data):
        """Check health data for alerts"""
        alerts = []
        if health_data.get('temperature', 72) < 68:
            alerts.append(self.send_alert('critical', 
                f'Temperature {health_data["temperature"]}°F < 68°F', 'health'))
        
        if health_data.get('sleep_hours', 7) < 6:
            alerts.append(self.send_alert('warning',
                f'Sleep {health_data["sleep_hours"]}h < 6h', 'health'))
        
        return alerts
    
    def check_ebay_alerts(self, ebay_data):
        """Check eBay data for alerts"""
        alerts = []
        listings = ebay_data.get('listings', [])
        
        for listing in listings:
            if listing.get('views', 0) > 50 and listing.get('watchers', 0) == 0:
                alerts.append(self.send_alert('info',
                    f'High views ({listing["views"]}) but no watchers', 'ebay'))
            
            if listing.get('days_active', 0) > 7 and listing.get('watchers', 0) == 0:
                alerts.append(self.send_alert('warning',
                    f'Listing {listing["id"]} active 7+ days with no watchers', 'ebay'))
        
        return alerts

# Global instance
alerts = AlertSystem()
