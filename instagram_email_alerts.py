#!/usr/bin/env python3
"""
Instagram Email Alerts
Sends email when posts exceed engagement thresholds
"""

import os
import json
import requests
from datetime import datetime, timedelta
from email_notifier import emailer

INSTAGRAM_API_URL = "https://graph.instagram.com"
ACCESS_TOKEN = open("instagram_token.txt").read().strip()

def get_recent_posts(hours_back=24):
    """Get posts from last X hours"""
    url = f"{INSTAGRAM_API_URL}/me/media"
    params = {
        "fields": "id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count",
        "access_token": ACCESS_TOKEN
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "data" not in data:
            print(f"❌ API error: {data}")
            return []
        
        # Filter for recent posts
        cutoff = datetime.now() - timedelta(hours=hours_back)
        recent = []
        
        for post in data["data"]:
            post_time = datetime.fromisoformat(post["timestamp"].replace("Z", "+00:00"))
            if post_time > cutoff:
                recent.append(post)
        
        return recent
        
    except Exception as e:
        print(f"❌ Error fetching posts: {e}")
        return []

def check_for_hot_posts(recent_posts):
    """Identify posts that exceed engagement thresholds"""
    hot_posts = []
    
    thresholds = {
        "like_count": 20,      # Email if >20 likes
        "comments_count": 5,    # Email if >5 comments
        "views": 500           # For video/reel views (if available)
    }
    
    for post in recent_posts:
        reasons = []
        
        if post.get("like_count", 0) > thresholds["like_count"]:
            reasons.append(f"{post['like_count']} likes")
        
        if post.get("comments_count", 0) > thresholds["comments_count"]:
            reasons.append(f"{post['comments_count']} comments")
        
        # Check for video views if media_type is VIDEO
        if post.get("media_type") in ["VIDEO", "REEL"]:
            # Would need additional API call for views
            pass
        
        if reasons:
            hot_posts.append({
                "id": post["id"],
                "permalink": post.get("permalink", ""),
                "caption": post.get("caption", "")[:100],
                "media_type": post.get("media_type", ""),
                "reasons": ", ".join(reasons),
                "timestamp": post.get("timestamp", "")
            })
    
    return hot_posts

def send_alert(hot_posts):
    """Send email alert for hot posts"""
    if not hot_posts:
        print("📭 No hot posts found")
        return
    
    subject = f"🔥 {len(hot_posts)} Instagram Posts Performing Well"
    
    body = f"""
INSTAGRAM ENGAGEMENT ALERT
{datetime.now().strftime('%Y-%m-%d %H:%M')}

Hot posts detected:

"""
    
    html_body = f"""
<h2>🔥 Instagram Engagement Alert</h2>
<p><strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</strong></p>

<h3>Hot Posts:</h3>
<ul>
"""
    
    for post in hot_posts:
        body += f"""
• {post['reasons']}
  Caption: {post['caption']}
  Link: {post['permalink']}
  Time: {post['timestamp']}
"""
        html_body += f"""
<li>
    <strong>{post['reasons']}</strong><br>
    Caption: {post['caption']}<br>
    <a href="{post['permalink']}">View on Instagram</a><br>
    <small>{post['timestamp']}</small>
</li>
"""
    
    html_body += "\n</ul>"
    
    # Add suggestions
    body += "\n\n💡 Suggestions:\n"
    body += "• Turn this into an eBay listing with similar subject\n"
    body += "• Create a YouTube Short about this post\n"
    body += "• Engage with commenters to build collectors\n"
    
    result = emailer.send_email(
        to_email="contact.regenesis.art@gmail.com",
        subject=subject,
        body=body,
        html_body=html_body
    )
    
    print(f"📧 Alert sent: {result}")

if __name__ == "__main__":
    print("🔍 Checking Instagram for hot posts...")
    recent = get_recent_posts(hours_back=24)
    print(f"Found {len(recent)} posts in last 24h")
    
    hot = check_for_hot_posts(recent)
    send_alert(hot)
