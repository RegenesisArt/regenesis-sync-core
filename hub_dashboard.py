#!/usr/bin/env python3
"""
Regenesis Hub Live Dashboard
Works WITHOUT redeployment - queries your live hub
"""
import requests
import json
from datetime import datetime

HUB_URL = "https://us-central1-regenesis-art-hub.cloudfunctions.net/regenesis-hub-v1"

def get_hub_status():
    """Get hub status"""
    try:
        r = requests.get(f"{HUB_URL}/", timeout=5)
        return r.json()
    except:
        return {"system": "unknown", "status": "offline"}

def get_ebay_status():
    """Get eBay integration status"""
    try:
        r = requests.get(f"{HUB_URL}/v1/ebay/status", timeout=5)
        return r.json()
    except:
        return {"ebay": "offline"}

def get_cmhp_state():
    """Get CMHP state"""
    try:
        r = requests.get(f"{HUB_URL}/v1/cmhp/state", timeout=5)
        return r.json()
    except:
        return {"pillars": {}, "genesis_quest": "unknown"}

def display_dashboard():
    """Display live dashboard"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║ 🕹️  REGENESIS HUB LIVE DASHBOARD                              ║")
    print("║ 📍 Hub: https://us-central1-regenesis-art-hub.cloudfunctions.net/regenesis-hub-v1        ║")
    print("║ 🕐 Time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "                   ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print("")
    
    # Get data from live hub
    hub = get_hub_status()
    ebay = get_ebay_status()
    cmhp = get_cmhp_state()
    
    print("┌───────────────────────── SYSTEM STATUS ─────────────────────────┐")
    print(f"│ • Hub:       {hub.get('system', 'Unknown'):<20} {hub.get('status', ''):<10} │")
    print(f"│ • eBay:      {'Integrated' if ebay.get('ebay') == 'ready' else 'Offline':<20} {ebay.get('environment', ''):<10} │")
    print(f"│ • Quest:     {'Active' if cmhp.get('genesis_quest') == 'ready' else 'Inactive':<20} {'Ready':<10} │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print("")
    
    print("┌───────────────────────── CMHP PILLARS ──────────────────────────┐")
    pillars = cmhp.get('pillars', {})
    active = sum(1 for v in pillars.values() if v == 'active')
    print(f"│ • Active: {active}/13 pillars {'█' * (active*2)}{'░' * ((13-active)*2)} {active*100//13}% │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print("")
    
    print("┌───────────────────────── GENESIS QUEST ─────────────────────────┐")
    print("│ • Subject:   Golden Retriever Portrait                         │")
    print("│ • Tier:      Tier 1 (Fast Art - $50-100)                       │")
    print("│ • APV:       $0 / $1,500  [░░░░░░░░░░░░░░░░░░░░] 0%            │")
    print("│ • Funds:     $0 / $6,000  [░░░░░░░░░░░░░░░░░░░░] 0%            │")
    print("│ • Timeline:  216 days remaining                                │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print("")
    
    print("┌───────────────────────── NEXT ACTIONS ──────────────────────────┐")
    print("│ 1. Begin Golden Retriever portrait painting                    │")
    print("│ 2. Record process for YouTube Short                            │")
    print("│ 3. APV starts accruing with first brushstroke                  │")
    print("│ 4. Hub will create eBay listing upon completion                │")
    print("└─────────────────────────────────────────────────────────────────┘")
    print("")
    
    print("💡 Your automation is LIVE. Paint → Hub → eBay → $6,000")

if __name__ == "__main__":
    display_dashboard()

# AI AGENT ENDPOINT
@app.route('/api/ai-query', methods=['POST'])
def ai_query():
    try:
        query = request.json.get('query', '')
        from simple_agent import CMHP_Agent
        agent = CMHP_Agent()
        response = agent.process_query(query)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': 'Error: ' + str(e)})
