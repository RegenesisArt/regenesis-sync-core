import os
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
import requests
import json
from datetime import datetime

HUB_URL = "http://10.88.0.3:8080/api/ebay-data"

class eBayRealTracker:
    def __init__(self):
        self.app_id = os.environ.get('EBAY_APP_ID')
        if not self.app_id:
            raise ValueError("EBAY_APP_ID not set in environment")
        
        # Initialize with real credentials
        self.api = Finding(
            appid=self.app_id,
            config_file=None,
            siteid="EBAY-US"
        )
    
    def search_completed(self, keywords, max_results=20):
        """Search REAL completed/sold listings"""
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
            print(f"🔍 Searching eBay for: {keywords}")
            response = self.api.execute('findCompletedItems', request)
            items = []
            
            if hasattr(response.reply, 'searchResult') and hasattr(response.reply.searchResult, 'item'):
                for item in response.reply.searchResult.item:
                    items.append({
                        'title': item.title,
                        'sold_price': float(item.sellingStatus.currentPrice.value),
                        'condition': item.condition.conditionDisplayName if hasattr(item, 'condition') else 'Unknown',
                        'url': item.viewItemURL,
                        'end_time': item.listingInfo.endTime,
                        'category': item.primaryCategory.categoryName
                    })
            
            print(f"✅ Found {len(items)} sold items")
            return items
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def get_active_listings(self, keywords, max_results=20):
        """Search active listings"""
        request = {
            'keywords': keywords,
            'paginationInput': {'entriesPerPage': max_results},
            'sortOrder': 'BestMatch'
        }
        
        try:
            print(f"🔍 Searching active listings for: {keywords}")
            response = self.api.execute('findItemsByKeywords', request)
            items = []
            
            if hasattr(response.reply, 'searchResult') and hasattr(response.reply.searchResult, 'item'):
                for item in response.reply.searchResult.item:
                    items.append({
                        'title': item.title,
                        'current_price': float(item.sellingStatus.currentPrice.value) if hasattr(item.sellingStatus, 'currentPrice') else 0,
                        'bid_count': item.sellingStatus.bidCount if hasattr(item.sellingStatus, 'bidCount') else 0,
                        'url': item.viewItemURL,
                        'category': item.primaryCategory.categoryName
                    })
            
            print(f"✅ Found {len(items)} active listings")
            return items
        except Exception as e:
            print(f"❌ Error: {e}")
            return []

def send_to_hub(data):
    """Send real data to hub"""
    try:
        response = requests.post(HUB_URL, json={
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'source': 'ebay_api_real'
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    tracker = eBayRealTracker()
    
    searches = [
        'original oil painting landscape',
        'pet portrait oil painting',
        'abstract expressionism painting',
        'still life oil painting original'
    ]
    
    all_results = {}
    
    for search in searches:
        sold = tracker.search_completed(search, 5)
        all_results[f"sold_{search.replace(' ', '_')}"] = sold
        
        active = tracker.get_active_listings(search, 5)
        all_results[f"active_{search.replace(' ', '_')}"] = active
    
    result = send_to_hub(all_results)
    print(f"\n📤 Sent to hub: {result}")
    
    print("\n📊 MARKET SUMMARY:")
    for key, items in all_results.items():
        if items:
            avg_price = sum(i.get('sold_price', i.get('current_price', 0)) for i in items) / len(items)
            print(f"  {key}: {len(items)} items, avg ${avg_price:.2f}")
