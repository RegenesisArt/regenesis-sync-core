"""
Unified platform manager
"""
from datetime import datetime

class PlatformManager:
    def __init__(self):
        self.platforms = {
            'ebay': {'status': 'mock', 'ready': True, 'revenue': 0},
            'etsy': {'status': 'mock', 'ready': True, 'revenue': 0},
            'patreon': {'status': 'mock', 'ready': True, 'revenue': 0},
            'youtube': {'status': 'mock', 'ready': True, 'revenue': 0},
            'instagram': {'status': 'mock', 'ready': True, 'revenue': 0},
            'twitter': {'status': 'mock', 'ready': True, 'revenue': 0}
        }
        
    def get_overview(self):
        """Get overview of all platforms"""
        total_revenue = sum(p['revenue'] for p in self.platforms.values())
        ready_platforms = [name for name, data in self.platforms.items() if data['ready']]
        
        return {
            'total_platforms': len(self.platforms),
            'ready_platforms': ready_platforms,
            'total_revenue': total_revenue,
            'platform_details': self.platforms,
            'recommendation': self._get_recommendation(),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _get_recommendation(self):
        """Get platform recommendation"""
        if self.platforms['ebay']['status'] == 'mock':
            return "Focus on eBay first (highest revenue potential for art)"
        elif sum(p['revenue'] for p in self.platforms.values()) < 100:
            return "Build audience on YouTube/Instagram while eBay processes"
        else:
            return "Expand to Etsy for prints and Patreon for subscriptions"
    
    def cross_post_content(self, content, platforms=None):
        """Cross-post content to multiple platforms"""
        if platforms is None:
            platforms = ['instagram', 'twitter']
        
        results = {}
        for platform in platforms:
            if platform in self.platforms:
                results[platform] = {
                    'success': True,
                    'message': f'Posted to {platform} (mock)',
                    'content_preview': content[:50] + '...'
                }
        
        return {
            'total_platforms': len(results),
            'results': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def schedule_weekly_content(self, artwork_data):
        """Schedule content across all platforms for the week"""
        schedule = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for i, day in enumerate(days):
            day_schedule = {
                'day': day,
                'platforms': {},
                'theme': self._get_day_theme(i)
            }
            
            # Instagram post
            if i % 2 == 0:  # Every other day
                day_schedule['platforms']['instagram'] = {
                    'type': 'image',
                    'content': f'Studio progress on {artwork_data.get("title", "my painting")}',
                    'time': '10:00 AM'
                }
            
            # Twitter posts
            day_schedule['platforms']['twitter'] = {
                'type': 'text',
                'content': self._get_twitter_content(i, artwork_data),
                'time': '2:00 PM'
            }
            
            # YouTube (once a week)
            if i == 2:  # Wednesday
                day_schedule['platforms']['youtube'] = {
                    'type': 'video',
                    'content': 'Weekly process update',
                    'time': '5:00 PM'
                }
            
            schedule.append(day_schedule)
        
        return schedule
    
    def _get_day_theme(self, day_index):
        themes = [
            'Process Monday', 'Technique Tuesday', 'Work-in-Progress Wednesday',
            'Throwback Thursday', 'Finished Friday', 'Studio Saturday', 'Sketch Sunday'
        ]
        return themes[day_index % len(themes)]
    
    def _get_twitter_content(self, day_index, artwork_data):
        tweets = [
            f"Working on '{artwork_data.get('title', 'my latest')}' today. The colors are coming together beautifully.",
            f"Art tip: Step back from your work every 20 minutes. Fresh perspective = better decisions.",
            f"Process shot: This detail took 3 hours but was worth it. #artprocess",
            f"What's inspiring your creativity today? For me, it's the changing light.",
            f"Just added the final glaze to '{artwork_data.get('title', 'this piece')}'. Magic moment.",
            f"Studio days are my favorite days. Nothing but paint and possibility.",
            f"Sunday sketching: Planning the next big piece. Ideas flowing."
        ]
        return tweets[day_index % len(tweets)]

# Global instance
platforms = PlatformManager()
