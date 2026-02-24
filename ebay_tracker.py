import os
from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
import requests
import json
from datetime import datetime

HUB_URL = "https://regenesis-hub-v8-510958561702.us-central1.run.app/api/ebay-data"

class eBayTracker:
    def __init__(self, app_id=None):
        self.app_id = app_id or os.getenv('EBAY_APP_ID')
        self.api = Finding(appid=self.app_id, config_file=None, siteid="EBAY-US")
    
    def search_completed(self, keywords, max_results=10):
        """Search completed listings for market research"""
        request = {
            'keywords': keywords,
            'itemFilter': [
                {'name': 'SoldItemsOnly', 'value': 'true'},
                {'name': 'CompletedItemsOnly', 'value': 'true'}
            ],
            'paginationInput': {'entriesPerPage': max_results}
        }
        
        try:
            response = self.api.execute('findCompletedItems', request)
            items = []
            
            if hasattr(response.reply, 'searchResult') and hasattr(response.reply.searchResult, 'item'):
                for item in response.reply.searchResult.item[:max_results]:
                    items.append({
                        'title': item.title,
                        'sold_price': float(item.sellingStatus.currentPrice.value),
                        'condition': item.condition.conditionDisplayName if hasattr(item, 'condition') else 'Unknown',
                        'listing_url': item.viewItemURL,
                        'end_time': item.listingInfo.endTime,
                        'category': item.primaryCategory.categoryName
                    })
            
            return items
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    def get_active_listings(self, keywords, max_results=10):
        """Search active listings"""
        request = {
            'keywords': keywords,
            'paginationInput': {'entriesPerPage': max_results}
        }
        
        try:
            response = self.api.execute('findItemsByKeywords', request)
            items = []
            
            if hasattr(response.reply, 'searchResult') and hasattr(response.reply.searchResult, 'item'):
                for item in response.reply.searchResult.item[:max_results]:
                    items.append({
                        'title': item.title,
                        'current_price': float(item.sellingStatus.currentPrice.value) if hasattr(item.sellingStatus, 'currentPrice') else 0,
                        'bid_count': item.sellingStatus.bidCount if hasattr(item.sellingStatus, 'bidCount') else 0,
                        'listing_url': item.viewItemURL,
                        'category': item.primaryCategory.categoryName
                    })
            
            return items
        except Exception as e:
            print(f"Error: {e}")
            return []

def send_to_hub(data):
    try:
        response = requests.post(HUB_URL, json={
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'source': 'ebay_api'
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    # You'll need an eBay App ID - get one free at https://developer.ebay.com/
    print("⚠️  You need an eBay App ID to use this.")
    print("Get one free at: https://developer.ebay.com/")
    print("Then set: export EBAY_APP_ID='your_app_id'")
    
    # For now, we'll create a mock version that reads from a file
    mock_data = {
        'pet_portraits': [
            {'title': 'Original Pet Portrait Oil Painting', 'sold_price': 95.00, 'condition': 'New'},
            {'title': 'Custom Dog Portrait', 'sold_price': 120.00, 'condition': 'New'},
        ],
        'landscapes': [
            {'title': 'Mountain Lake Oil Painting', 'sold_price': 210.00, 'condition': 'New'},
            {'title': 'Sunset Landscape Original Art', 'sold_price': 85.00, 'condition': 'New'},
        ]
    }
    
    result = send_to_hub(mock_data)
    print(f"📤 Hub response: {result}")
