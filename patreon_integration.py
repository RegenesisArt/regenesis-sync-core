"""
Patreon integration (mock)
"""
from datetime import datetime

class PatreonMockAPI:
    def __init__(self):
        self.tiers = [
            {'name': 'Supporter', 'price': 5, 'subscribers': 0, 'benefits': ['Process photos']},
            {'name': 'Collector', 'price': 15, 'subscribers': 0, 'benefits': ['Process photos', 'Digital sketches']},
            {'name': 'Patron', 'price': 30, 'subscribers': 0, 'benefits': ['All above', 'Monthly Q&A']},
            {'name': 'Visionary', 'price': 100, 'subscribers': 0, 'benefits': ['All above', 'Commission discount']}
        ]
        self.posts = []
    
    def get_stats(self):
        total = sum(tier['subscribers'] for tier in self.tiers)
        revenue = sum(tier['subscribers'] * tier['price'] for tier in self.tiers)
        
        return {
            'platform': 'patreon',
            'status': 'mock_mode',
            'total_subscribers': total,
            'monthly_revenue': revenue,
            'tiers': self.tiers,
            'posts_count': len(self.posts),
            'ready_for_real': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def create_post(self, content, tier_access='all'):
        """Create mock Patreon post"""
        post_id = f'post_{len(self.posts) + 1:03d}'
        post = {
            'id': post_id,
            'content': content[:100] + '...' if len(content) > 100 else content,
            'tier_access': tier_access,
            'created': datetime.utcnow().isoformat(),
            'views': 0,
            'comments': 0
        }
        self.posts.append(post)
        return {'success': True, 'post_id': post_id, 'mode': 'mock'}

# Global instance
patreon = PatreonMockAPI()
