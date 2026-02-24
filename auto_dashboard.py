#!/usr/bin/env python3
"""
REAL Automation Dashboard - Shows live data from your hub
"""
import requests
import json
from datetime import datetime

HUB_URL = "https://us-central1-regenesis-art-hub.cloudfunctions.net/regenesis-hub-v1"

def get_data(endpoint):
    """Get data from hub"""
    try:
        r = requests.get(f"{HUB_URL}{endpoint}", timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def post_data(endpoint, data):
    """Post data to hub"""
    try:
        r = requests.post(f"{HUB_URL}{endpoint}", 
                         json=data, 
                         timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def display_progress_bar(percentage, width=20):
    """Display progress bar"""
    filled = int(percentage / 100 * width)
    empty = width - filled
    return "█" * filled + "░" * empty

def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║ 🚀 REAL-TIME AUTOMATION DASHBOARD                              ║")
    print(f"║ 📍 Hub: {HUB_URL}")
    print(f"║ 🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("")
    
    # Get REAL data from hub
    print("┌───────────────────────── LIVE DATA ──────────────────────────────┐")
    
    # Hub status
    hub_status = get_data("/")
    print(f"│ • Hub Status:  {hub_status.get('status', 'unknown'):<15} {hub_status.get('system', 'Unknown'):<30} │")
    
    # Financial data
    financial = get_data("/v1/financial")
    if "financial" in financial:
        fin = financial["financial"]
        apv_total = fin.get("apv_total", 0)
        total_current = fin.get("total_current", 0)
        total_target = fin.get("total_target", 16000)
        progress = fin.get("progress_percentage", 0)
        
        print(f"│ • APV Accrued: ${apv_total:<6.0f} {'':<10} Total: ${total_current:.0f}/${total_target} │")
        print(f"│ • Progress:    {progress:.1f}% {display_progress_bar(progress)} │")
        
        # The Key progress
        the_key = fin.get("the_key", {})
        key_current = the_key.get("current", 0)
        key_target = the_key.get("target", 6000)
        key_progress = (key_current / key_target * 100) if key_target > 0 else 0
        
        print(f"│ • The Key:     ${key_current:.0f}/${key_target} {display_progress_bar(key_progress, 10)} │")
    
    # Artworks data
    artworks = get_data("/v1/artworks")
    if "artworks" in artworks:
        count = artworks.get("count", 0)
        art_list = artworks.get("artworks", [])
        
        print(f"│ • Artworks:    {count} total {'':<10} {len([a for a in art_list if a.get('status') == 'in_progress'])} in progress │")
        
        # Show latest artwork
        if art_list:
            latest = art_list[-1]  # Most recent
            title = latest.get("title", "Unknown")[:25]
            apv = latest.get("current_apv", 0)
            target = latest.get("target_price", 100)
            progress = (apv / target * 100) if target > 0 else 0
            
            print(f"│ • Latest:      {title:<25} ${apv:.0f}/${target} │")
            print(f"│ • Progress:    {progress:.1f}% {display_progress_bar(progress)} │")
    
    # eBay status
    ebay = get_data("/v1/ebay/status")
    if "ebay" in ebay:
        ebay_status = ebay["ebay"].get("status", "unknown")
        listings_ready = ebay["ebay"].get("listings_ready", 0)
        print(f"│ • eBay:        {ebay_status:<10} {listings_ready} listings ready │")
    
    print("└─────────────────────────────────────────────────────────────────┘")
    print("")
    
    # Commands section
    print("┌───────────────────────── QUICK COMMANDS ────────────────────────┐")
    print("│ Commands to run in terminal:                                    │")
    print("│                                                                 │")
    print("│ 1. Log painting hours:                                          │")
    print("│    curl -X POST {HUB_URL}/v1/artworks/[ID]/log \\")
    print("│      -H \"Content-Type: application/json\" \\")
    print("│      -d '{\"hours\":2,\"description\":\"Painting session\"}'")
    print("│                                                                 │")
    print("│ 2. Create new artwork:                                          │")
    print("│    curl -X POST {HUB_URL}/v1/artworks \\")
    print("│      -H \"Content-Type: application/json\" \\")
    print("│      -d '{\"title\":\"New Painting\",\"tier\":1,\"target_price\":200}'")
    print("│                                                                 │")
    print("│ 3. Generate eBay listing:                                       │")
    print("│    curl -X POST {HUB_URL}/v1/ebay/listing/[ID]")
    print("│                                                                 │")
    print("│ 4. View financials:                                             │")
    print("│    curl {HUB_URL}/v1/financial")
    print("└─────────────────────────────────────────────────────────────────┘")
    print("")
    print("💡 Your automation hub is ACTIVE. Paint → APV → eBay → $")
    print(f"💡 Latest artwork ID: art_20260205_215347")

if __name__ == "__main__":
    main()
