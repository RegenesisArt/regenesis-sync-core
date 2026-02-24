"""
Etsy API integration (mock for now)
"""
from datetime import datetime

class EtsyMockAPI:
    def __init__(self):
        self.mock_listings = [
            {
                'id': 'etsy_001',
                'title': 'Art Print - Genesis Quest',
                'price': 45.00,
                'views': 128,
                'favorites': 12,
                'status': 'active',
                'type': 'print'
            },
            {
                'id': 'etsy_002', 
                'title': 'Original Painting - Test',
                'price': 350.00,
                'views': 56,
                'favorites': 3,
                'status': 'draft',
                'type': 'original'
            }
        ]
    
    def get_listings(self):
        return {
            'platform': 'etsy',
            'status': 'mock_mode',
            'listings': self.mock_listings,
            'total_revenue': 0,
            'ready_for_real': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def create_listing(self, artwork_data, listing_type='print'):
        """Create mock Etsy listing"""
        new_id = f'etsy_{len(self.mock_listings) + 1:03d}'
        listing = {
            'id': new_id,
            'title': artwork_data.get('title', 'Untitled Art'),
            'price': artwork_data.get('price', 50.00),
            'views': 0,
            'favorites': 0,
            'status': 'draft',
            'type': listing_type,
            'created': datetime.utcnow().isoformat()
        }
        self.mock_listings.append(listing)
        return {'success': True, 'listing_id': new_id, 'mode': 'mock'}

# Global instance
etsy = EtsyMockAPI()
