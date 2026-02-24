#!/usr/bin/env python3
"""
VISUAL AUTOMATION DASHBOARD
"""
import requests
import json
from datetime import datetime, timedelta
import time
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()
HUB = "https://us-central1-regenesis-art-hub.cloudfunctions.net/regenesis-hub-v1"

def get_hub_data():
    """Get all data from hub"""
    data = {
        "hub": {},
        "financial": {},
        "artworks": [],
        "ebay": {},
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        r = requests.get(HUB, timeout=3)
        data["hub"] = r.json()
    except:
        data["hub"] = {"status": "offline"}
    
    try:
        r = requests.get(f"{HUB}/v1/financial", timeout=3)
        data["financial"] = r.json().get("financial", {})
    except:
        data["financial"] = {}
    
    try:
        r = requests.get(f"{HUB}/v1/artworks", timeout=3)
        resp = r.json()
        data["artworks"] = resp.get("artworks", [])
        data["artworks_count"] = resp.get("count", 0)
    except:
        data["artworks"] = []
    
    return data
