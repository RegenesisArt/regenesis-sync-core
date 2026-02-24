import os
import requests
import json
from datetime import datetime

HUB_URL = "https://regenesis-hub-v8-510958561702.us-central1.run.app"
TOKEN_FILE = "instagram_token.txt"

def get_token():
    """Get Instagram token from file or env"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return os.environ.get('INSTAGRAM_TOKEN')

def fetch_instagram_data():
    """Fetch Instagram insights"""
    token = get_token()
    if not token:
        print("❌ No Instagram token found")
        return None
    
    # Get user info
    user_url = "https://graph.instagram.com/me"
    params = {
        'fields': 'id,username,account_type,media_count',
        'access_token': token
    }
    
    try:
        user_resp = requests.get(user_url, params=params)
        user_data = user_resp.json()
        
        # Get recent media
        media_url = "https://graph.instagram.com/me/media"
        media_params = {
            'fields': 'id,caption,media_type,media_url,permalink,timestamp,like_count,comments_count',
            'access_token': token,
            'limit': 5
        }
        
        media_resp = requests.get(media_url, params=media_params)
        media_data = media_resp.json()
        
        return {
            'user': user_data,
            'media': media_data.get('data', []),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def send_to_hub(data):
    """Send Instagram data to hub"""
    try:
        response = requests.post(f"{HUB_URL}/api/instagram-data", json={
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'source': 'instagram_automation'
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    try:
        print("📸 Fetching Instagram data...")
        data = fetch_instagram_data()
        
        if data:
            print(f"✅ User: {data['user'].get('username')}")
            print(f"📊 Media count: {data['user'].get('media_count', 0)}")
            print(f"🖼️ Recent posts: {len(data.get('media', []))}")
            
            result = send_to_hub(data)
            print(f"📤 Hub response: {result}")
        else:
            print("❌ Failed to fetch Instagram data")
            
    except Exception as e:
        import traceback
        import requests
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ ERROR: {error_msg}")
        
        # Report to hub error endpoint
        try:
            requests.post("http://10.88.0.3:8080/api/log-error", json={
                'script': 'instagram_automation.py',
                'error': error_msg,
                'context': {
                    'stage': 'main_execution',
                    'error_type': type(e).__name__
                }
            })
            print("📤 Error reported to hub")
        except:
            print("❌ Could not report error to hub")
