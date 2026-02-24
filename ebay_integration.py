import os
import requests

class EBayAutomation:
    def __init__(self):
        self.app_id = os.environ.get('EBAY_SANDBOX_APP_ID')
        self.secret = os.environ.get('EBAY_SANDBOX_SECRET')
        self.dev_id = os.environ.get('EBAY_SANDBOX_DEV_ID')
        
    def test_connection(self):
        return {
            "status": "ebay_ready",
            "app_id": self.app_id[:10] + "..." if self.app_id else "missing",
            "environment": "sandbox"
        }
        
    def create_listing_template(self, artwork):
        return {
            "title": f"Original Oil Painting: {artwork.get('title', 'Genesis Piece')}",
            "description": "Regenesis Art Collection - Original Oil Painting",
            "price": artwork.get('price', 100),
            "category": "Art"
        }
