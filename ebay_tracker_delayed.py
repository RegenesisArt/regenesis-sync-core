import os
import time
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
import requests
import json
from datetime import datetime

HUB_URL = "https://regenesis-hub-v8-510958561702.us-central1.run.app/api/ebay-data"

class eBayTracker:
    def __init__(self):
        self.app_id = os.environ.get('EBAY_APP_ID')
        if not self.app_id:
            raise ValueError("EBAY_APP_ID not set in environment")
        
        self.api = Finding(
            appid=self.app_id,
            config_file=None,
            siteid="EBAY-US"
        )
    
    def search_completed(self, keywords, max_results=5):
        """Search completed listings with delay to avoid rate limits"""
        time.sleep(1)  # 1 second delay between calls
        request = {
            'keywords': keywords,
            'itemFilter': [
                {'name': 'SoldItemsOnly', 'value': 'true'},
                {'name': 'CompletedItemsOnly', 'value': 'true'}
            ],
            'paginationInput': {'entriesPerPage': max_results},
            'sortOrder': 'EndTimeSoonest'
        }
        
        try:
            print(f"🔍 Searching: {keywords}")
            response = self.api.execute('findCompletedItems', request)
            items = []
            
            if hasattr(response.reply, 'searchResult') and hasattr(response.reply.searchResult, 'item'):
                for item in response.reply.searchResult.item:
                    items.append({
                        'title': item.title,
                        'sold_price': float(item.sellingStatus.currentPrice.value),
                        'condition': item.condition.conditionDisplayName if hasattr(item, 'condition') else 'Unknown',
                        'url': item.viewItemURL,
                        'category': item.primaryCategory.categoryName
                    })
            
            print(f"✅ Found {len(items)} items")
            return items
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

if __name__ == '__main__':
    try:
        tracker = eBayTracker()
        
        # Just test one search first
        results = tracker.search_completed('original oil painting landscape', 3)
        
        if results:
            print("\n📊 SAMPLE RESULTS:")
            for item in results:
                print(f"  • {item['title']} - ${item['sold_price']}")
            
            # Send to hub
            result = requests.post(HUB_URL, json={
                'data': {'test_results': results},
                'timestamp': datetime.now().isoformat(),
                'source': 'ebay_test'
            })
            print(f"\n📤 Sent to hub: {result.json()}")
        else:
            print("No results yet — rate limit may still be active. Try again in a few minutes.")
            
    except Exception as e:
        import traceback
        import requests
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ ERROR: {error_msg}")
        
        # Report to hub error endpoint
        try:
            requests.post("http://10.88.0.3:8080/api/log-error", json={
                'script': 'ebay_tracker_delayed.py',
                'error': error_msg,
                'context': {
                    'stage': 'main_execution',
                    'error_type': type(e).__name__
                }
            })
            print("📤 Error reported to hub")
        except:
            print("❌ Could not report error to hub")
