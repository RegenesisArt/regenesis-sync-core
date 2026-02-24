import json
import re
import requests
from datetime import datetime

HUB_URL = "https://regenesis-hub-v8-510958561702.us-central1.run.app"

def scan_email_for_payment(email):
    """Scan email for payment information"""
    subject = email.get('subject', '').lower()
    sender = email.get('sender', '').lower()
    snippet = email.get('snippet', '').lower()
    
    # Payment indicators
    payment_keywords = ['payment', 'receipt', 'invoice', 'sold', 'sale', 'paid', 
                        'transaction', 'confirmed', 'completed', 'order', 'receipt',
                        'your order', 'you received', 'money received', 'payment sent']
    platforms = ['paypal', 'stripe', 'etsy', 'ebay', 'shopify', 'gumroad', 'patreon',
                 'square', 'venmo', 'zelle', 'cash app']
    
    is_payment = any(k in subject for k in payment_keywords) or any(p in sender for p in platforms)
    
    # Extract amount
    amount = None
    if is_payment:
        # Look for $ amounts
        dollar_pattern = r'\$(\d+(?:\.\d{2})?)'
        amounts = re.findall(dollar_pattern, subject + ' ' + snippet)
        if amounts:
            try:
                amount = float(amounts[0])
            except:
                pass
    
    return {
        'is_payment': is_payment,
        'amount': amount,
        'platform': next((p for p in platforms if p in sender or p in subject), 'unknown'),
        'email_id': email.get('id', ''),
        'subject': subject[:50] + '...' if len(subject) > 50 else subject
    }

def update_the_key(amount, platform, subject):
    """Send payment to hub"""
    try:
        response = requests.post(f"{HUB_URL}/api/update-key", json={
            'amount': amount,
            'platform': platform,
            'subject': subject,
            'timestamp': datetime.now().isoformat()
        })
        return response.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    try:
        # Get latest emails from hub
        response = requests.get(f"{HUB_URL}/state/latest")
        data = response.json()
        
        emails = data.get('email_ingestion', {}).get('last_batch', [])
        print(f"📧 Scanning {len(emails)} recent emails for payments...")
        
        total_found = 0
        total_amount = 0
        
        for email in emails:
            result = scan_email_for_payment(email)
            if result['is_payment'] and result['amount']:
                print(f"💰 PAYMENT FOUND: ${result['amount']} from {result['platform']}")
                print(f"   Subject: {result['subject']}")
                update_result = update_the_key(result['amount'], result['platform'], result['subject'])
                print(f"   Hub: {update_result}")
                total_found += 1
                total_amount += result['amount']
        
        if total_found > 0:
            print(f"\n✅ TOTAL: {total_found} payments, ${total_amount}")
        else:
            print("\n✅ No new payments found")
            
    except Exception as e:
        import traceback
        import requests
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ ERROR: {error_msg}")
        
        # Report to hub error endpoint
        try:
            requests.post("http://10.88.0.3:8080/api/log-error", json={
                'script': 'payment_detector.py',
                'error': error_msg,
                'context': {
                    'stage': 'main_execution',
                    'error_type': type(e).__name__
                }
            })
            print("📤 Error reported to hub")
        except:
            print("❌ Could not report error to hub")
