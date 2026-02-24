import os
import requests
from googleapiclient.discovery import build
from datetime import datetime

HUB_URL = "https://regenesis-hub-v8-510958561702.us-central1.run.app"
API_KEY = os.environ.get('YOUTUBE_API_KEY', '')
CHANNEL_ID = 'YOUR_CHANNEL_ID'  # Replace with your channel ID

def get_channel_stats():
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Get channel statistics
    channel_resp = youtube.channels().list(
        part='statistics,snippet',
        id=CHANNEL_ID
    ).execute()
    
    if not channel_resp['items']:
        return None
    
    channel = channel_resp['items'][0]
    stats = channel['statistics']
    
    # Get recent videos
    videos_resp = youtube.search().list(
        part='id,snippet',
        channelId=CHANNEL_ID,
        maxResults=5,
        order='date'
    ).execute()
    
    videos = []
    for item in videos_resp.get('items', []):
        if item['id']['kind'] == 'youtube#video':
            video_id = item['id']['videoId']
            video_stats = youtube.videos().list(
                part='statistics',
                id=video_id
            ).execute()
            
            if video_stats['items']:
                stats = video_stats['items'][0]['statistics']
                videos.append({
                    'title': item['snippet']['title'],
                    'video_id': video_id,
                    'view_count': stats.get('viewCount', 0),
                    'like_count': stats.get('likeCount', 0),
                    'comment_count': stats.get('commentCount', 0),
                    'published_at': item['snippet']['publishedAt']
                })
    
    return {
        'channel': {
            'title': channel['snippet']['title'],
            'subscriber_count': stats.get('subscriberCount', 0),
            'video_count': stats.get('videoCount', 0),
            'view_count': stats.get('viewCount', 0)
        },
        'recent_videos': videos,
        'timestamp': datetime.now().isoformat()
    }

def send_to_hub(data):
    try:
        response = requests.post(f"{HUB_URL}/api/youtube-data", json=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    try:
        if not API_KEY:
            print("❌ Please set YOUTUBE_API_KEY environment variable")
            exit(1)
        
        print("📺 Fetching YouTube data...")
        data = get_channel_stats()
        if data:
            print(f"✅ Channel: {data['channel']['title']}")
            print(f"   Subscribers: {data['channel']['subscriber_count']}")
            print(f"   Videos: {data['channel']['video_count']}")
            result = send_to_hub(data)
            print(f"📤 Hub response: {result}")
        else:
            print("❌ Failed to fetch YouTube data")
            
    except Exception as e:
        import traceback
        import requests
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ ERROR: {error_msg}")
        
        # Report to hub error endpoint
        try:
            requests.post("http://10.88.0.3:8080/api/log-error", json={
                'script': 'youtube_automation.py',
                'error': error_msg,
                'context': {
                    'stage': 'main_execution',
                    'error_type': type(e).__name__
                }
            })
            print("📤 Error reported to hub")
        except:
            print("❌ Could not report error to hub")
