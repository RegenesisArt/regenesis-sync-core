#!/usr/bin/env python3
import requests, json
from datetime import datetime

HUB = "https://us-central1-regenesis-art-hub.cloudfunctions.net/regenesis-hub-v1"

print("\n" + "="*60)
print("🚀 DEEPSEEK BUSINESS AUTOMATION DASHBOARD")
print("="*60)

# Test hub
try:
    r = requests.get(HUB, timeout=5)
    print(f"✅ Hub: {r.json().get('status', 'online')}")
except:
    print("❌ Hub: Offline")

# Get financials
try:
    r = requests.get(f"{HUB}/v1/financial", timeout=5)
    data = r.json().get('financial', {})
    apv = data.get('apv_total', 0)
    print(f"💰 APV: ${apv}")
except:
    print("💰 APV: Error")

# Get artworks
try:
    r = requests.get(f"{HUB}/v1/artworks", timeout=5)
    data = r.json()
    count = data.get('count', 0)
    print(f"🎨 Artworks: {count}")
    if data.get('artworks'):
        art = data['artworks'][-1]
        print(f"   Latest: {art.get('title', '?')}")
        print(f"   APV: ${art.get('current_apv', 0)}")
except:
    print("🎨 Artworks: Error")

print("\n💡 Run: python3 dashboard.py (updates live)")
print("="*60)
