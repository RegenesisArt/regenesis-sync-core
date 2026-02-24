#!/usr/bin/env python3
"""
Simple script to update CMHP rules without full redeploy.
Adds 5 more rules to the existing hub logic.
"""
import requests
import json

HUB_URL = "https://regenesis-hub-v1-510958561702.us-central1.run.app"

# 5 additional CMHP rules to add
NEW_RULES = [
    {
        "id": "pricing_rule_1",
        "condition": {"pillar": "financial_escape", "field": "apv", "operator": ">", "value": 500},
        "action": {"type": "unlock", "platform": "etsy", "message": "APV > $500: Etsy unlocked. Need $0.20.", "priority": "medium"}
    },
    {
        "id": "content_rule_1", 
        "condition": {"pillar": "artistic_ascent", "field": "progress", "operator": ">", "value": 25},
        "action": {"type": "generate", "content": "youtube_short", "message": "Progress >25%: Make YouTube short", "priority": "medium"}
    },
    {
        "id": "health_rule_2",
        "condition": {"pillar": "bodily_regeneration", "field": "temperature", "operator": "<", "value": 70},
        "action": {"type": "emergency", "message": "Temp <70°F: Warmth protocol!", "priority": "critical"}
    },
    {
        "id": "temporal_rule_1",
        "condition": {"pillar": "temporal", "field": "days_remaining", "operator": "<", "value": 180},
        "action": {"type": "alert", "message": "<180 days: Accelerate!", "priority": "high"}
    },
    {
        "id": "financial_rule_2",
        "condition": {"pillar": "financial_escape", "field": "the_key", "operator": ">=", "value": 6000},
        "action": {"type": "celebrate", "message": "🎉 $6,000 REACHED!", "priority": "critical"}
    }
]

def add_rules_via_logging():
    """Add new rules by logging them as events that the hub can process."""
    print("Adding 5 new CMHP rules via event logging...")
    
    for rule in NEW_RULES:
        response = requests.post(
            f"{HUB_URL}/log",
            json={
                "type": "cmhp_rule_add",
                "rule": rule,
                "note": "Adding new rule to automation system"
            },
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ Rule added: {rule['id']}")
        else:
            print(f"❌ Failed to add {rule['id']}: {response.text}")
    
    print("\n🎯 Total rules should now be: 8 (3 original + 5 new)")
    print("Check: curl -s https://regenesis-hub-v1-510958561702.us-central1.run.app/cmhp/rules | python3 -m json.tool")

if __name__ == "__main__":
    add_rules_via_logging()
