"""
Social media automation
"""
from datetime import datetime
import random

class SocialAutomation:
    def __init__(self):
        self.platforms = ['twitter', 'instagram', 'tiktok', 'youtube']
        self.content_types = ['process', 'finished', 'inspiration', 'tips']
        
    def generate_post(self, artwork_data, content_type=None):
        """Generate social media post"""
        if not content_type:
            content_type = random.choice(self.content_types)
        
        templates = {
            'process': [
                "🖌️ In the studio today: Working on '{title}'. The light is perfect for capturing these details.",
                "🎨 Process shot: This is where the magic happens. '{title}' coming to life.",
                "✨ Behind the brush: Today's session on '{title}'. Every stroke matters."
            ],
            'finished': [
                "🎉 JUST FINISHED: '{title}' is complete! Available now.",
                "🌟 New artwork alert: '{title}' is finished and looking incredible.",
                "✅ Completed: '{title}'. This piece tells a powerful story."
            ],
            'inspiration': [
                "💡 Today's inspiration: The way light transforms ordinary moments.",
                "🌅 Finding beauty in the everyday - that's what drives my art.",
                "✨ What inspires you? For me, it's the interplay of shadow and light."
            ],
            'tips': [
                "🔥 Pro tip: Don't be afraid to make 'ugly' art. It's part of the process.",
                "🎨 Technique tip: Try painting with your non-dominant hand for interesting textures.",
                "💫 Remember: Your unique perspective is your greatest asset as an artist."
            ]
        }
        
        template = random.choice(templates[content_type])
        post = template.format(
            title=artwork_data.get('title', 'my latest piece'),
            price=artwork_data.get('price', 100)
        )
        
        # Add hashtags
        hashtags = ['#art', '#painting', '#artist', '#oilpainting', '#artistsoninstagram']
        if 'regenesis' in artwork_data.get('title', '').lower():
            hashtags.append('#regenesisart')
        
        return {
            'content': f"{post}\n\n{' '.join(hashtags[:3])}",
            'platforms': ['instagram', 'twitter'],
            'content_type': content_type,
            'scheduled_time': datetime.utcnow().isoformat(),
            'hashtags': hashtags
        }
    
    def auto_schedule_posts(self, artwork_list, days=7):
        """Auto-schedule posts for the week"""
        schedule = []
        for i in range(days):
            post = self.generate_post(
                artwork_data=random.choice(artwork_list) if artwork_list else {'title': 'my artwork'},
                content_type=random.choice(self.content_types)
            )
            schedule.append({
                'day': i + 1,
                'post': post,
                'time': f"{10 + i % 8}:00"  # Spread throughout day
            })
        return schedule

# Global instance
social = SocialAutomation()
