#!/usr/bin/env python3
"""
eBay Hot Subjects Email Alerts
Sends email when high-demand art subjects are found
"""

import os
import json
import sys
from datetime import datetime
from email_notifier import emailer

def check_for_hot_subjects(results_file="ebay_mock_data.json"):
    """Check eBay results for hot subjects and send email alerts"""
    
    if not os.path.exists(results_file):
        print(f"❌ No results file found: {results_file}")
        return
    
    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading results file: {e}")
        return
    
    # Look for hot subjects
    hot_subjects = []
    
    for category, items in data.items():
        for item in items:
            # Define "hot" criteria
            if (item.get('totalSold', 0) > 10 and 
                item.get('avgPrice', 0) > 100 and
                item.get('sellThroughRate', 0) > 30):
                
                hot_subjects.append({
                    'category': category,
                    'title': item.get('title', 'Unknown'),
                    'sold': item.get('totalSold', 0),
                    'avg_price': item.get('avgPrice', 0),
                    'sell_through': item.get('sellThroughRate', 0),
                    'url': item.get('url', '')
                })
    
    if not hot_subjects:
        print("📭 No hot subjects found this run")
        return
    
    # Sort by sell-through rate (hottest first)
    hot_subjects.sort(key=lambda x: x['sell_through'], reverse=True)
    
    # Build email
    subject = f"🔥 {len(hot_subjects)} Hot eBay Art Subjects Found"
    
    body = f"""
EBAY HOT SUBJECTS ALERT
{datetime.now().strftime('%Y-%m-%d %H:%M')}

Top {len(hot_subjects)} high-demand art subjects:

"""
    
    html_body = f"""
<h2>🔥 eBay Hot Subjects Alert</h2>
<p><strong>{datetime.now().strftime('%Y-%m-%d %H:%M')}</strong></p>

<h3>Top {len(hot_subjects)} High-Demand Art Subjects:</h3>
<ul>
"""
    
    for i, subject in enumerate(hot_subjects[:5], 1):
        body += f"""
{i}. {subject['title']}
   • Sold: {subject['sold']} items
   • Avg Price: ${subject['avg_price']:.2f}
   • Sell-through: {subject['sell_through']}%
   • Category: {subject['category']}
"""
        html_body += f"""
<li>
    <strong>{i}. {subject['title']}</strong><br>
    • Sold: {subject['sold']} items<br>
    • Avg Price: ${subject['avg_price']:.2f}<br>
    • Sell-through: {subject['sell_through']}%<br>
    • Category: {subject['category']}
</li>
"""
    
    html_body += "\n</ul>"
    
    # Send email
    result = emailer.send_email(
        to_email="contact.regenesis.art@gmail.com",
        subject=subject,
        body=body,
        html_body=html_body
    )
    
    print(f"📧 Hot subjects alert sent: {result}")

if __name__ == "__main__":
    check_for_hot_subjects()
