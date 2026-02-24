"""
Financial tracking for CMHP Pillar 3
"""
from datetime import datetime

class FinancialTracker:
    def __init__(self):
        self.mock_finances = {
            'revenue_today': 0,
            'revenue_week': 0,
            'revenue_month': 0,
            'expenses_today': 0,
            'cash_balance': 0,
            'the_key_progress': 0,  # $0/$6,000
            'freedom_fuel_progress': 0  # $0/$10,000
        }
    
    def update_from_ebay(self, ebay_data):
        """Update finances from eBay sales"""
        # This will connect to real eBay API later
        pass
    
    def get_financial_status(self):
        """Get current financial status"""
        status = self.mock_finances.copy()
        status['timestamp'] = datetime.utcnow().isoformat()
        status['days_remaining'] = 216  # From master clock
        status['daily_target'] = 27.78  # $6,000 / 216 days
        return status

# Global instance
finances = FinancialTracker()
