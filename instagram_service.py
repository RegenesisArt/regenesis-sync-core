import os
import requests
import json
from datetime import datetime

def fetch_recent_media(limit=10):
    """Fetch recent media posts from Instagram"""
    token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    ig_id = os.environ.get('INSTAGRAM_BUSINESS_ID', '17841480605462784')
    
    if not token:
        return {"error": "Missing Instagram access token"}
    
    url = f"https://graph.facebook.com/v18.0/{ig_id}/media"
    params = {
        'fields': 'id,caption,media_type,media_url,permalink,timestamp,comments_count,like_count',
        'access_token': token,
        'limit': limit
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": str(e)}

def fetch_insights(metric='impressions,reach,profile_views', period='day'):
    """Fetch Instagram insights"""
    token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    ig_id = os.environ.get('INSTAGRAM_BUSINESS_ID', '17841480605462784')
    
    if not token:
        return {"error": "Missing Instagram access token"}
    
    url = f"https://graph.facebook.com/v18.0/{ig_id}/insights"
    params = {
        'metric': metric,
        'period': period,
        'access_token': token
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def save_to_file(data, filename='instagram_latest.json'):
    """Save data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    return filename
