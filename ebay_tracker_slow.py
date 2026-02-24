import os
import time
from ebaysdk.finding import Connection as Finding
import requests
from datetime import datetime

HUB_URL = "http://10.88.0.3:8080/api/ebay-data"

class eBayTracker:
    def __init__(self):
        self.app_id = os.environ.get('EBAY_APP_ID')
        if not self.app_id:
            raise ValueError("EBAY_APP_ID not set")
        
        self.api = Finding(appid=self.app_id, config_file=None, siteid="EBAY-US")
    
    def search_completed(self, keywords, max_results=3):
        time.sleep(3)  # 3 seconds delay
        request = {
            'keywords': keywords,
            'itemFilter': [
                {'name': 'SoldItemsOnly', 'value': 'true'},
                {'name': 'CompletedItemsOnly', 'value': 'true'}
            ],
            'paginationInput': {'entriesPerPage': max_results}
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
                        'url': item.viewItemURL
                    })
            return items
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

if __name__ == '__main__':
    tracker = eBayTracker()
    
    # Try just one search
    results = tracker.search_completed('original oil painting', 2)
    
    if results:
        print(f"\n✅ Found {len(results)} items:")
        for r in results:
            print(f"  • {r['title']} - ${r['sold_price']}")
    else:
        print("\n⏳ Still rate limited. Try again in an hour.")
